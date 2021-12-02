from flask import Flask
from pymongo import MongoClient
from dotenv import load_dotenv
import ssl
import os


load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

# Connecting to database
url = os.environ.get('MONGODB_URI')
client = MongoClient(url, ssl_cert_reqs=ssl.CERT_NONE)
db = client['myFlaskApp']
