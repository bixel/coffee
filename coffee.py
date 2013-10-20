# encoding: utf-8

from __future__ import division

from datetime import datetime
import ldap
from wtforms import StringField, PasswordField

from flask import Flask, render_template, redirect, request, g, url_for
from flask.ext.login import LoginManager, login_user, logout_user, current_user, login_required
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.admin import Admin
from flask.ext.admin.contrib.sqlamodel import ModelView
from flask.ext.wtf import Form

app = Flask(__name__)
login_manager = LoginManager()
app.config.from_object('config')
app.config.from_envvar('COFFEE_SETTINGS', silent=True)

db = SQLAlchemy(app)
admin = Admin(app)
login_manager.init_app(app)

def init_db():
    db.create_all()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    name = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)
    payments = db.relationship('Payment', backref='user', lazy='dynamic')
    consumptions = db.relationship('Consumption', backref='user', lazy='dynamic')

    def __init__(self, name=None, username=None, email=None):
        if name:
            self.name = name
        if username:
            self.username = username
        if email:
            self.email = email

    def __repr__(self):
        return '<User %r>' % self.username

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Integer)
    date = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, amount=None, date=None):
        if amount:
            self.amount = amount
        if not date:
            self.date = datetime.utcnow()
        else:
            self.date = date

    def __repr__(self):
        return '<Payment %r>' % self.id

class Consumption(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    units = db.Column(db.Integer)
    amountPaid = db.Column(db.Integer)
    date = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, units=None, amountPaid=None, date=None):
        if units:
            self.units = units
        if not amountPaid:
            self.amountPaid = units * app.config['COFFEE_PRICE']
        else:
            self.amountPaid = amountPaid
        if not date:
            self.date = datetime.utcnow()
        else:
            self.date = date

    def __repr__(self):
        return '<Consumption %r>' % self.id

class BudgetChange(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Integer)
    description = db.Column(db.String(200))

    def __init__(self, amount=None, description=None):
        if amount:
            self.amount = amount
        if description:
            self.description = description

    def __repr__(self):
        return '<BudgetChange %r>' % self.description

class LoginForm(Form):
    username = StringField('Username')
    password = PasswordField('Password')

@app.before_request
def before_request():
    g.user = current_user

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route('/budget')
def budget():
    changes = db.session.query(BudgetChange).all()
    s = 0
    for c in changes:
        s += c.amount
    return str(s)

@app.route('/budget/<username>')
def budget_user(username):
    user = db.session.query(User).filter_by(username=username).first()
    s = 0
    for c in user.consumptions:
        s += c.amountPaid
    for p in user.payments:
        s += p.amount
    return str(s)

@app.route('/', methods=['GET', 'POST'])
def index():
    form = LoginForm()
    changes = db.session.query(BudgetChange).all()
    s = 0
    for c in changes:
        s += c.amount
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = db.session.query(User).filter_by(username=username).first()
        login_user(user)
        #ldap_login(username, password)
        return redirect(url_for("personal"))
    return render_template("global.html", form=form, current_budget=render_euros(s))

@app.route('/personal')
def personal():
    if g.user is not None and g.user.is_authenticated():
        data = dict()

        for p in g.user.payments:
            data[str(p.date.date())] = render_euros(p.amount)
        for c in g.user.consumptions:
            data[str(c.date.date())] = render_euros(c.amountPaid)

        changes = []
        for k in sorted(data):
            changes.append((k, data[k]))

        return render_template('user.html', changes=changes)
    else:
        return redirect(url_for('index'))

#def ldap_login(username, password):
#    if is_in_ldap(username) and authenticate(username, password):
#        user = db.session.query(User).filter_by(username=username).first()
#        if user:
#            login_user(user)
#        else:
#            user = User(username=username, email=...)
#        login_user(user)
#        return True

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('index'))

def render_euros(num):
    euros = num // 100
    cents = num % 100
    return (u'€ {}.{}'.format(euros, cents))

admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Payment, db.session))
admin.add_view(ModelView(Consumption, db.session))

if __name__ == '__main__':
    app.run()
