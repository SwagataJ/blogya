import smtplib
import ssl
import os
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import url_for
from tokens import generate_token
import json
import urllib.request
import certifi

load_dotenv()


def validate_email(email):
    api_key = os.environ.get('REALEMAIL_API_KEY')
    url = 'https://realemail.expeditedaddons.com/?api_key=' + \
          api_key + '&email=' + email + '&fix_typos=false'
    resp = urllib.request.urlopen(url, context=ssl.create_default_context(
        cafile=certifi.where())).read().decode('utf-8')
    json_acceptable_string = resp.replace("'", "\"")
    response = json.loads(json_acceptable_string)
    return response['valid'] and not response['is_disposable']


def send_email_register(receiver_email, user):
    port = 587
    smtp_server = "email-smtp.us-west-1.amazonaws.com"
    sender_email = "no_reply@blogya.live"
    username = os.environ.get('MAILERTOGO_USERNAME')
    password = os.environ.get('MAILERTOGO_PASSWORD')

    message = MIMEMultipart("alternative")
    message["Subject"] = "Welcome to BLOGYA!"
    message["From"] = "Team Blogya <{email}>".format(email=sender_email)
    message["To"] = receiver_email

    text = """\
    Hi, {}
    
    Welcome to BLOGYA. We are so excited to have you.
    
    Believe it or not, you've got the power to create beautiful blogs. The kind of blogs that make people stop and 
    say, \"Wow, you wrote that?!"
    
    It's free and astonishingly easy to use.
    
    What are you going to create?""".format(user)

    html = """\
    <html>
      <body>
        <p>Hi, <i>{}</i></p>
        <p> Welcome to BLOGYA. We are so excited to have you. </p>
        <p> Believe it or not, you've got the power to create beautiful blogs. The kind of blogs that make people stop 
        and say, \"Wow, you wrote that?!" </p>
        <p> It's free and astonishingly easy to use.</p> 
        <p> What are you going to create? </p>
      </body>
    </html>
    """.format(user)

    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    message.attach(part1)
    message.attach(part2)

    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_server, port) as server:
        server.starttls(context=context)
        server.login(username, password)
        server.sendmail(sender_email, receiver_email, message.as_string())


def send_email_reset(user):
    port = 587
    smtp_server = "email-smtp.us-west-1.amazonaws.com"
    sender_email = "reset@blogya.live"
    username = os.environ.get('MAILERTOGO_USERNAME')
    password = os.environ.get('MAILERTOGO_PASSWORD')

    message = MIMEMultipart("alternative")
    message["Subject"] = "Password Reset Request"
    message["From"] = "Team Blogya <{email}>".format(email=sender_email)
    message["To"] = user['Email']

    serial = generate_token(user['Email'])
    link = url_for('reset_token', token=serial, _external=True)

    text = """\
    Hi {name},
    As you have requested for reset password instructions, here they are, please follow the URL:
    [Reset Password]({url})
    Alternatively, open the following url in your browser:
    {url}""".format(name=user['Name'], url=link)

    html = """\
    <html>
    <body>
        <p>Hi {name},</p>
        <p>As you have requested for reset password instructions, here they
 are, please follow the URL:</p>
        <p><a href="{url}">Reset Password</a></p>
        <p>Alternatively, open the following url in your browser</p>
        <p>
            <pre>{url}</pre>
        </p>
        </body>
        </html>
        """.format(name=user['Name'], url=link)
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    message.attach(part1)
    message.attach(part2)

    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_server, port) as server:
        server.starttls(context=context)
        server.login(username, password)
        # server.sendmail(sender_email, user['Email'], message.as_string())
        server.sendmail(sender_email, user['Email'], message.as_string())
