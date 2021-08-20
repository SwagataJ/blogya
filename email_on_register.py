import smtplib
import ssl
import os
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv()


def send_email(receiver_email, user):
    port = 587
    smtp_server = "email-smtp.us-east-1.amazonaws.com"
    sender_email = "no_reply@blogya.live"
    username = os.environ.get('MAILERTOGO_USERNAME')
    password = os.environ.get('MAILERTOGO_PASSWORD')

    message = MIMEMultipart("alternative")
    message["Subject"] = "Welcome to BLOGYA!"
    message["From"] = sender_email
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


