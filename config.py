import os

DEBUG = os.environ.get("COFFEE_DEBUG", True) == True
USE_LDAP = os.environ.get("COFFEE_LDAP", True) == True
SECRET_KEY = 'p:0+\'.p)X_(p'
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.environ.get('COFFEE_DB', 'coffee.db')
COFFEE_PRICES = [
    [30, u'Kaffee'],
    [50, u'Milchkaffee']
]

LDAP_HOST = 'e5pc51.physik.tu-dortmund.de'
LDAP_SEARCH_BASE = 'cn=users,dc=e5,dc=physik,dc=uni-dortmund,dc=de'
LDAP_PORT = 389

SERVER = os.environ.get('COFFEE_SERVER', 'localhost')
PORT = os.environ.get('COFFEE_PORT', 5000)

MAIL_SERVER = 'unimail.uni-dortmund.de'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = 'smigbabu'
MAIL_PASSWORD = 'i4subpih'
MAIL_DEFAULT_SENDER = 'igor.babuschkin@udo.edu'

BUDGET_WARN_BELOW = 0
