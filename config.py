import os
import sys

DEBUG = os.environ.get("COFFEE_DEBUG", 'False').lower() == 'true'
USE_LDAP = os.environ.get("COFFEE_LDAP", 'True').lower() == 'true'
SECRET_KEY = os.environ.get('COFFEE_SECRET_KEY')
COFFEE_PRICES = [
    [30, u'Kaffee'],
    [50, u'Milchkaffee']
]

MONGODB_DB = os.environ.get('COFFEE_DB_NAME', 'coffeedb')
MONGODB_HOST = os.environ.get('COFFEE_DB_HOST', '127.0.0.1')
MONGODB_PORT = os.environ.get('COFFEE_DB_PORT', 27017)
MONGODB_TZ_AWARE = True

LDAP_HOST = os.environ.get('COFFEE_LDAP_HOST', 'localhost')
LDAP_SEARCH_BASE = os.environ.get('COFFEE_LDAP_SEARCH_BASE', 'ou=people,dc=coffee,dc=ldap')
LDAP_SEARCH_BIND = os.environ.get('COFFEE_LDAP_SEARCH_BIND')
LDAP_SEARCH_PASSWORD = os.environ.get('COFFEE_LDAP_SEARCH_PASSWORD')
LDAP_PORT = os.environ.get('COFFEE_LDAP_PORT', 389)
LDAP_TLS = os.environ.get('COFFEE_LDAP_TLS', 'true').lower() == 'true'

SERVER = os.environ.get('COFFEE_SERVER', 'localhost')
PORT = os.environ.get('COFFEE_PORT', 5000)

MAIL_SERVER = os.environ.get('COFFEE_MAILSERVER')
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = os.environ.get('COFFEE_MAILUSER')
MAIL_PASSWORD = os.environ.get('COFFEE_PASSWORD')
MAIL_DEFAULT_SENDER = os.environ.get('COFFEE_MAILADDRESS', 'admin@coffee.dev')
MAIL_MINISTER_NAME = os.environ.get('COFFEE_MINISTER_NAME', 'Mr. Minister')

BUDGET_WARN_BELOW = 0

BASEURL = os.environ.get('COFFEE_BASEURL', '')

TZ = os.environ.get('COFFEE_TIMEZONE', 'Europe/Berlin')

ACHIEVEMENT_PROFESSIONAL_STALKER_NAME = os.environ.get('ACHIEVEMENT_PROFESSIONAL_STALKER_NAME', 'testuser')
