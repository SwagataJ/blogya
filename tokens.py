from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from __init__ import app, db


def generate_token(email):
    s = Serializer(app.config['SECRET_KEY'], expires_in=3600)
    return s.dumps({'Email': email}).decode('utf-8')


def verify_token(token):
    s = Serializer(app.config['SECRET_KEY'])
    try:
        email = s.loads(token)['Email']
    except:
        return None
    return db['users'].find_one({'Email': email})
