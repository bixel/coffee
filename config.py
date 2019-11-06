import os
import sys

DEBUG = os.environ.get("COFFEE_DEBUG", 'False') == 'True'
USE_LDAP = os.environ.get("COFFEE_LDAP", 'True') == 'True'
SECRET_KEY = os.environ.get('COFFEE_SECRET_KEY', 'super_secret')
if SECRET_KEY == 'super_secret' and not DEBUG:
    print('Warning: Please set a secret key in production.')
COFFEE_PRICES = [
    [35, u'Kaffee'],
    [50, u'Milchkaffee']
]

DB_HOST = os.environ.get('COFFEE_DB_HOST', '127.0.0.1')
DB_PORT = os.environ.get('COFFEE_DB_PORT', 27017)

LDAP_HOST = os.environ.get('COFFEE_LDAP_HOST')
LDAP_SEARCH_BASE = os.environ.get('COFFEE_LDAP_SEARCH')
LDAP_PORT = 389

SERVER = os.environ.get('COFFEE_SERVER', 'localhost')
PORT = os.environ.get('COFFEE_PORT', 5000)

MAIL_SERVER = os.environ.get('COFFEE_MAILSERVER')
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = os.environ.get('COFFEE_MAILUSER')
MAIL_PASSWORD = os.environ.get('COFFEE_PASSWORD')
MAIL_DEFAULT_SENDER = os.environ.get('COFFEE_MAILADDRESS', 'admin@coffee.dev')

BUDGET_WARN_BELOW = 0

BASEURL = os.environ.get('COFFEE_BASEURL', '')

TZ = os.environ.get('COFFEE_TIMEZONE', 'Europe/Berlin')
