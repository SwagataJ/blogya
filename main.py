from datetime import datetime
from functools import wraps
from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from wtforms.fields.html5 import EmailField
from pymongo import MongoClient
import ssl
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

# Connecting to database
url = os.environ.get('MONGODB_URI')
client = MongoClient(url, ssl_cert_reqs=ssl.CERT_NONE)
db = client['myFlaskApp']


# HomePage
@app.route('/')
def index():
    return render_template('index.html')


# About
@app.route('/about')
def about():
    return render_template('about.html')


# Articles
@app.route('/articles')
def articles():
    articlelist = db['articles'].find()
    if articlelist.count() > 0:
        return render_template('articles.html', articles=articlelist)
    else:
        msg = 'No article found'
        return render_template('articles.html', msg=msg)


# Single Article
@app.route('/article/<string:id>/')
def article(id):
    articlewithid = db['articles'].find_one({'id': id})
    return render_template('article.html', article=articlewithid)


# Registration Form
class RegisterForm(Form):
    name = StringField('Name', [validators.DataRequired(), validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.DataRequired(), validators.Length(min=4, max=25)])
    email = EmailField('Email address', [validators.DataRequired(), validators.Email()])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match.')
    ])
    confirm = PasswordField('Confirm Password')


# Registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        existing_username = db['users'].find({'username': form.username.data})
        existing_email = db['users'].find(({'Email': form.email.data}))

        # Adding user's details to database
        if existing_username.count() == 0 and existing_email.count() == 0:
            db['users'].insert_one({
                'Name': form.name.data,
                'Email': form.email.data,
                'username': form.username.data,
                'password': sha256_crypt.encrypt(str(form.password.data))
            })

            flash('You are now registered and can login', 'success')
            return redirect(url_for('login'))
        else:
            if existing_email.count() != 0:
                flash('Email is already being used.')
            elif existing_username.count() != 0:
                flash('Username is already taken.')
    return render_template('register.html', form=form)


# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password_candidate = request.form['password']
        user = db['users'].find_one({'username': username})

        # Checking if user exists
        if user is not None:
            password = user['password']

            # Checking the password
            if sha256_crypt.verify(password_candidate, password):
                session['logged_in'] = True
                session['username'] = username
                session['name'] = db['users'].find_one({'username': username})['Name']

                flash('You are now logged in.', 'success')
                return redirect(url_for('dashboard'))
            else:
                error = 'Invalid login.'
                return render_template('login.html', error=error)
        else:
            error = 'Username does not exist. Please register.'
            return render_template('login.html', error=error)
    return render_template('login.html')


# Check if user is logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))

    return wrap


# Logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out.', 'success')
    return redirect(url_for('login'))


# Dashboard
@app.route('/dashboard')
@is_logged_in
def dashboard():
    articlelist = db['articles'].find({'Author-username': session['username']})
    if articlelist.count() > 0:
        return render_template('dashboard.html', articles=articlelist)
    else:
        msg = 'No article found'
        return render_template('dashboard.html', msg=msg)


# Article Form Class
class ArticleForm(Form):
    title = StringField('Title', [validators.Length(min=1, max=200)])
    body = TextAreaField('Body', [validators.Length(min=30)])


# Add Article
@app.route('/add_article', methods=['GET', 'POST'])
@is_logged_in
def add_article():
    form = ArticleForm(request.form)
    if request.method == 'POST' and form.validate():
        db['articles'].insert_one({
            'id': os.urandom(4).hex(),
            'Title': form.title.data,
            'Body': form.body.data,
            'Author': db['users'].find_one({'username': session['username']})['Name'],
            'Author-username': session['username'],
            'Date': datetime.now().strftime("%d/%m/%Y")
        })

        flash('Article Created', 'success')
        return redirect(url_for('dashboard'))

    return render_template('add_article.html', form=form)


# Edit Article
@app.route('/edit_article/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def edit_article(id):
    # Get article by id
    article_to_edit = db['articles'].find_one({'id': id})

    # Get form
    form = ArticleForm(request.form)

    # Populate article form fields
    form.title.data = article_to_edit['Title']
    form.body.data = article_to_edit['Body']

    if request.method == 'POST' and form.validate():
        title = request.form['title']
        body = request.form['body']

        db['articles'].update_one({'id': id}, {"$set": {
            'Title': title,
            'Body': body
        }})

        flash('Article Updated', 'success')

        return redirect(url_for('dashboard'))

    return render_template('edit_article.html', form=form)


# Delete Article
@app.route('/delete_article/<string:id>', methods=['POST'])
@is_logged_in
def delete_article(id):
    db['articles'].remove({'id': id})

    flash('Article Deleted', 'success')

    return redirect(url_for('dashboard'))
