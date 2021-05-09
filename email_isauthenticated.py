import json
import ssl
import urllib.request
import certifi
import os


def validate_email(email):
    api_key = os.environ.get('REALEMAIL_API_KEY')
    url = 'https://realemail.expeditedaddons.com/?api_key=' + 
        api_key + '&email=' + email + '&fix_typos=false'
    resp = urllib.request.urlopen(url, context=ssl.create_default_context(
        cafile=certifi.where())).read().decode('utf-8')
    json_acceptable_string = resp.replace("'", "\"")
    response = json.loads(json_acceptable_string)
    return response['valid'] and not response['is_disposable']
