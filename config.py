import os
import sys

DEBUG = os.environ.get("DEBUG", 'False').lower() == 'true'
USE_LDAP = os.environ.get("LDAP", 'True').lower() == 'true'
SECRET_KEY = os.environ.get('SECRET_KEY')
COFFEE_PRICES = [
    [30, u'Kaffee'],
    [50, u'Milchkaffee']
]

MONGODB_DB = os.environ.get('DB_NAME', 'coffeedb')
MONGODB_HOST = os.environ.get('DB_HOST', '127.0.0.1')
MONGODB_PORT = os.environ.get('DB_PORT', 27017)
MONGODB_TZ_AWARE = True

LDAP_HOST = os.environ.get('LDAP_HOST', 'localhost')
LDAP_SEARCH_BASE = os.environ.get('LDAP_SEARCH_BASE', 'ou=people,dc=coffee,dc=ldap')
LDAP_SEARCH_BIND = os.environ.get('LDAP_SEARCH_BIND')
LDAP_SEARCH_PASSWORD = os.environ.get('LDAP_SEARCH_PASSWORD')
LDAP_PORT = os.environ.get('LDAP_PORT', 389)
LDAP_TLS = os.environ.get('LDAP_TLS', 'true').lower() == 'true'

SERVER = os.environ.get('SERVER', 'localhost')
PORT = os.environ.get('PORT', 5000)

MAIL_SERVER = os.environ.get('MAILSERVER')
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = os.environ.get('MAILUSER')
MAIL_PASSWORD = os.environ.get('PASSWORD')
MAIL_DEFAULT_SENDER = os.environ.get('MAILADDRESS', 'admin@coffee.dev')
MAIL_MINISTER_NAME = os.environ.get('MINISTER_NAME', 'Mr. Minister')

BUDGET_WARN_BELOW = 0

BASEURL = os.environ.get('BASEURL', '')

TZ = os.environ.get('TIMEZONE', 'Europe/Berlin')

ENABLE_ACHIEVEMENTS = os.environ.get('ENABLE_ACHIEVEMENTS', 'true').lower() == 'true'
ACHIEVEMENT_PROFESSIONAL_STALKER_NAME = os.environ.get('ACHIEVEMENT_PROFESSIONAL_STALKER_NAME', 'testuser')
