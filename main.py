from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from wtforms.fields.html5 import EmailField
from pymongo import MongoClient
import ssl
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(12).hex()


# Connecting to database
url = os.environ.get('MONGODB_URI')
client = MongoClient(url, ssl_cert_reqs=ssl.CERT_NONE)
db = client['myFlaskApp']
users = db['users']


# HomePage
@app.route('/')
def index():
    return render_template('index.html')


# About
@app.route('/about')
def about():
    return render_template('about.html')


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
    if request.method == 'POST':
        existing_username = users.find({'username': form.username.data})
        existing_email = users.find(({'Email': form.email.data}))

        # Adding user's details to database
        if existing_username.count() == 0 and existing_email.count() == 0:
            users.insert_one({
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
        user = users.find_one({'username': username})

        # Checking if user exists
        if user is not None:
            password = user['password']

            # Checking the password
            if sha256_crypt.verify(password_candidate, password):
                session['logged_in'] = True
                session['username'] = username

                flash('You are now logged in.', 'success')
                return redirect(url_for('dashboard'))
            else:
                error = 'Invalid login.'
                return render_template('login.html', error=error)
        else:
            error = 'Username does not exist. Please register.'
            return render_template('login.html', error=error)
    return render_template('login.html')


# Logout
@app.route('/logout')
def logout():
    session['logged_in'] = False
    flash('You are now logged out.', 'success')
    return redirect(url_for('login'))


# Dashboard
@app.route('/dashboard')
def dashboard():
    if session['logged_in']:
        return render_template('dashboard.html')
    return redirect(url_for('login'))
