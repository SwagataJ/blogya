from wtforms import Form, StringField, TextAreaField, PasswordField, validators, SubmitField
from wtforms.fields.html5 import EmailField


# Registration Form
class RegisterForm(Form):
    name = StringField(
        'Name', [validators.DataRequired(), validators.Length(min=1, max=50)])
    username = StringField(
        'Username', [validators.DataRequired(), validators.Length(min=4, max=25)])
    email = EmailField('Email address', [
        validators.DataRequired(), validators.Email()])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match.')
    ])
    confirm = PasswordField('Confirm Password')


# Login Form
class LoginForm(Form):
    username = StringField(
        'Username', [validators.DataRequired(), validators.Length(min=4, max=25)])
    password = PasswordField('Password', [validators.DataRequired()])


# Reset Password Form
class ResetPasswordForm(Form):
    email = EmailField('Email address', [validators.DataRequired(), validators.Email()])


# Article Form Class
class ArticleForm(Form):
    title = StringField('Title', [validators.Length(min=1, max=200)])
    body = TextAreaField('Body', [validators.Length(min=30)])


class ResetPasswordFormAfterTokenAuth(Form):
    password = PasswordField('Password', validators=[validators.DataRequired(),
                                                     validators.EqualTo('confirm', message='Passwords do not match.')])
    confirm = PasswordField('Confirm Password')
