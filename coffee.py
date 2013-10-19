
from datetime import datetime

from flask import Flask
from flask_login import LoginManager

from flask.ext.sqlalchemy import SQLAlchemy

from flask.ext.admin import Admin
from flask.ext.admin.contrib.sqla import ModelView

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config.from_object('config')
app.config.from_envvar('COFFEE_SETTINGS', silent=True)
host, port = '', 5000

db = SQLAlchemy(app)

admin = Admin(app)

def init_db():
    db.create_all()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)
    payments = db.relationship('Payment', backref='user', lazy='dynamic')
    uses = db.relationship('Consumption', backref='user', lazy='dynamic')

    def __init__(self, username='', email=''):
        self.username = username
        self.email = email

    def __repr__(self):
        return '<User %r>' % self.username

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Integer)
    date = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, user_id=0, amount=0):
        self.amount = amount
        self.user_id = user_id
        self.date = datetime.utcnow()

    def __repr__(self):
        return '<Payment %r>' % self.id


class Consumption(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    units = db.Column(db.Integer)
    amountPaid = db.Column(db.Integer)
    date = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, user_id=0, units=0):
        self.units = units
        self.user_id = user_id
        self.amountPaid = units * app.config['COFFEE_PRICE']
        self.date = datetime.utcnow()

    def __repr__(self):
        return '<Consumption %r>' % self.id

@app.route('/')
def index_page():
    return 'Hello, World!'

@app.route('/add/<name>')
def add(name):
    user = User(name, name + '@test.com')
    db.session.add(user)
    db.session.commit()
    return 'Worked fine.'

def login_user():
    pass

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # login and validate the user...
        login_user(user)
        return redirect(request.args.get("next") or url_for("index"))
    return render_template("login.html", form=form)

admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Payment, db.session))
admin.add_view(ModelView(Consumption, db.session))

if __name__ == '__main__':
    app.run()
