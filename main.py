from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from wtforms.fields.html5 import EmailField
from pymongo import MongoClient
import ssl

app = Flask(__name__)
url = "mongodb+srv://swagata:tupai@cluster0.fyurl.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
client = MongoClient(url, ssl_cert_reqs=ssl.CERT_NONE)
db = client['myFlaskApp']
users = db['users']


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


'''@app.route('/articles')
def articles():
    return render_template('articles.html', articles=Articles)


@app.route('/article/<string:id>/')
def article(id):
    return render_template('article.html', id=id)'''


class RegisterForm(Form):
    name = StringField('Name', [validators.DataRequired(), validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.DataRequired(), validators.Length(min=4, max=25)])
    email = EmailField('Email address', [validators.DataRequired(), validators.Email()])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match.')
    ])
    confirm = PasswordField('Confirm Password')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST':
        existing_username = users.find({'username': form.username.data})
        existing_email = users.find(({'Email': form.email.data}))

        if existing_username.count() == 0 and existing_email.count() == 0:
            users.insert_one({
                'Name': form.name.data,
                'Email': form.email.data,
                'username': form.username.data,
                'password': sha256_crypt.encrypt(str(form.password.data))
            })

            flash('You are now registered and can login', 'success')
            return redirect(url_for('index'))
        else:
            if existing_email.count() != 0:
                flash('Email is already being used.')
            elif existing_username.count() != 0:
                flash('Username is already taken.')
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password_candidate = request.form['password']
    return render_template('login.html')
