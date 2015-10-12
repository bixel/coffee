# coding: utf-8

from __future__ import division, unicode_literals

from datetime import datetime, timedelta
import ldap
from wtforms import (StringField,
                     PasswordField,
                     BooleanField,
                     IntegerField,
                     HiddenField,
                     FieldList,
                     FormField,
                     SelectField,
                     TextField)
from wtforms.fields.html5 import DateField

import json

from jinja2 import evalcontextfilter

from flask import (Flask,
                   render_template,
                   redirect,
                   g,
                   url_for,
                   request,
                   send_from_directory,
                   flash,
                   abort)
from flask.ext.login import (LoginManager,
                             login_user,
                             logout_user,
                             current_user,
                             login_required)
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.wtf import Form
from flask.ext.mail import Mail, Message
from flask.ext.admin import Admin
from flask.ext.admin.contrib.sqla import ModelView

import codecs

from subprocess import Popen

app = Flask(__name__)
login_manager = LoginManager()
app.config.from_object('config')
app.config.from_envvar('COFFEE_SETTINGS', silent=True)
admin = Admin(app, name='E5 MoCA DB ADMIN', template_mode='bootstrap3')


class MyView(ModelView):
    def __init__(self, model, session, **kwargs):
        super(MyView, self).__init__(model, session, **kwargs)

    def is_accessible(self):
        valid = False
        try:
            valid = is_admin(g.user.username)
        except:
            pass
        return valid

db = SQLAlchemy(app)
login_manager.init_app(app)

mail = Mail()
mail.init_app(app)


def is_admin(uname):
    return uname in ['ibabuschking',
                     'tschmelzer',
                     'kheinicke']


def init_db():
    db.create_all()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    name = db.Column(db.Unicode(80), unique=True)
    email = db.Column(db.String(120), unique=True)
    payments = db.relationship('Payment', backref='user', lazy='dynamic')
    consumptions = db.relationship('Consumption', backref='user',
                                   lazy='dynamic')
    services = db.relationship('Service', backref='user', lazy='dynamic')

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

    @property
    def balance(self):
        s = 0
        for p in self.payments:
            s += p.amount
        for c in self.consumptions:
            s += c.amountPaid
        return s


class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Integer)
    date = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    budgetChanges = db.relationship('BudgetChange', backref='Payment',
                                    lazy='dynamic')

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
            self.amountPaid = -units * app.config['COFFEE_PRICE']
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
    date = db.Column(db.DateTime)
    payment_id = db.Column(db.Integer, db.ForeignKey('payment.id'))

    def __init__(self, amount=None, description=None, date=None):
        if amount:
            self.amount = amount
        if description:
            self.description = description
        if not date:
            self.date = datetime.utcnow()
        else:
            self.date = date

    def __repr__(self):
        return '<BudgetChange %r>' % self.description


class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    service_count = db.Column(db.Integer)

    def __init__(self, start=None, end=None, user_id=None, service_count=None):
        self.start_date = start or datetime.utcnow()
        self.end_date = end or self.start_date + timedelta(days=5)
        self.user_id = user_id
        self.service_count = (service_count
                              or (self.end_date - self.start_date).days)

    def __repr__(self):
        return '<Service {} to {}>'.format(self.start_date, self.end_date)


admin.add_view(MyView(User, db.session))
admin.add_view(MyView(Payment, db.session))
admin.add_view(MyView(Consumption, db.session))
admin.add_view(MyView(BudgetChange, db.session))
admin.add_view(MyView(Service, db.session))


class LoginForm(Form):
    username = StringField('Username')
    password = PasswordField('Password')
    remember = BooleanField('remember', default=False)


class PaymentForm(Form):
    users = sorted(db.session.query(User).all(), key=lambda x: x.name)
    ids = map(lambda x: x.id, users)
    names = map(lambda x: '{}{}'.format(x.name, (' ✉️' if x.email else '')),
                users)
    uid = SelectField('Name', choices=zip(ids, names), coerce=int)
    amount = IntegerField('Amount')


class ConsumptionFormBase(Form):
    users = sorted(db.session.query(User).all(), key=lambda x: x.name)
    ids = map(lambda x: x.id, users)
    names = map(lambda x: '{}{}'.format(x.name, (' ✉️' if x.email else '')),
                users)


class ConsumptionForm(ConsumptionFormBase):
    uid = SelectField(
        'Name',
        choices=zip(ConsumptionFormBase.ids, ConsumptionFormBase.names),
        coerce=int
    )
    units = IntegerField('Units')
    prices = SelectField('Price', choices=app.config['COFFEE_PRICES'],
                         coerce=int)


class ConsumptionSingleForm(Form):
    user = HiddenField()
    consumptions = FieldList(IntegerField('consumption'),
                             min_entries=len(app.config['COFFEE_PRICES']))


class ConsumptionListForm(Form):
    users = FieldList(FormField(ConsumptionSingleForm))


class ExpenseForm(Form):
    description = TextField('Description')
    amount = IntegerField('Amount')
    date = DateField('Date', default=datetime.utcnow)


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


@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    coffee_prices = app.config['COFFEE_PRICES']
    changes = db.session.query(BudgetChange).all()
    credits = db.session.query(User).all()

    s = 0
    credit = 0
    for c in changes:
        s += c.amount
    for c in credits:
        credit -= c.balance

    return render_template(
        "global.html", current_budget=render_euros(s),
        actual_budget=render_euros(s + credit),
        coffee_prices=coffee_prices
    )


@app.route('/personal')
@login_required
def personal():
    balance = g.user.balance
    color = ""
    if balance > 0:
        color = "green"
    elif balance < 0:
        color = "red"

    return render_template('user.html', current_balance=render_euros(balance),
                           balance_color=color)


@app.route('/personal_data.json')
@login_required
def personal_data():
    data = []

    for p in g.user.payments:
        data.append((p.date, p.amount))
    for c in g.user.consumptions:
        data.append((c.date, c.amountPaid))

    result = []
    for (d, a) in sorted(data, key=lambda x: x[0], reverse=True):
        result.append({'date': str(d.date()), 'amount': a})

    return json.dumps(result)


@app.route('/global_data.json')
@login_required
def global_data():
    changes = db.session.query(BudgetChange).all()
    li = []
    for c in changes:
        li.append((str(c.date.date()), c.amount, c.description))
    result = []
    for l in sorted(li, key=lambda x: x[0]):
        result.append({'date': l[0], 'amount': l[1], 'description': l[2]})
    return json.dumps(result)


def ldap_login(username, password, remember=False):
    data = ldap_authenticate(username, password)
    if data:
        user = db.session.query(User).filter_by(username=username).first()
        if not user:
            user = User(username=username)
            db.session.add(user)
        user.name = unicode(data['cn'][0], 'utf-8')
        try:
            user.email = data['mail'][0]
        except KeyError:
            print('A user has no mail entry in LDAP!')
        db.session.commit()
        login_user(user, remember=remember)
        return True
    else:
        return False


@app.route("/login", methods=['GET', 'POST'])
def login():
    if g.user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        remember = form.remember.data
        # user = db.session.query(User).filter_by(username=username).first()
        if not ldap_login(username, password, remember=remember):
            return '<h1>Login failed</h1>'
        return redirect(url_for('index'))
    return render_template('login.html', form=form)


def get_listofshame():
    users = db.session.query(User).all()
    entries = []
    for u in users:
        entries.append({'name': u.name, 'balance': u.balance})
    li = sorted(entries, key=lambda e: e['balance'])
    return li


@app.route("/administrate/interactive")
@login_required
def admin():
    if is_admin(g.user.username):
        pform = PaymentForm()
        cform = ConsumptionForm()
        eform = ExpenseForm()
        listofshame = get_listofshame()
        return render_template('admin.html', payment_form=pform,
                               consumption_form=cform, expense_form=eform,
                               list_of_shame=listofshame)
    else:
        return abort(403)


@app.route("/administrate/payment", methods=['POST'])
@login_required
def administrate_payment():
    if is_admin(g.user.username):
        pform = PaymentForm()
        if pform.validate_on_submit():
            uid = pform.uid.data
            amount = pform.amount.data
            user = db.session.query(User).filter_by(id=uid).first()
            payment = Payment(amount=amount)
            user.payments.append(payment)
            bc = BudgetChange(amount=amount,
                              description='Payment from ' + user.name)
            payment.budgetChanges.append(bc)
            db.session.add(bc)
            db.session.commit()
            if user.email:
                msg = Message(u"[Kaffeeministerium] Einzahlung von %s"
                              % render_euros(amount))
                msg.charset = 'utf-8'
                msg.add_recipient(user.email)
                msg.body = render_template('mail/payment',
                                           amount=render_euros(amount),
                                           balance=render_euros(user.balance))
                if not app.config['DEBUG']:
                    mail.send(msg)
                else:
                    print(u'Sending mail \n{}'.format(unicode(msg.as_string(),
                                                              'utf-8')))

            return redirect(url_for('admin'))
    else:
        return abort(403)


@app.route("/administrate/consumption", methods=['POST'])
@login_required
def administrate_consumption():
    if is_admin(g.user.username):
        cform = ConsumptionForm()
        if cform.validate_on_submit():
            uid = cform.uid.data
            units = cform.units.data
            user = db.session.query(User).filter_by(id=uid).first()
            price = cform.prices.data
            user.consumptions.append(Consumption(units=units,
                                     amountPaid=-units * price))
            db.session.commit()
            if user.balance < app.config['BUDGET_WARN_BELOW'] and user.email:
                msg = Message(u"[Kaffeeministerium] Geringes Guthaben!")
                msg.charset = 'utf-8'
                msg.add_recipient(user.email)
                msg.body = render_template('mail/lowbudget',
                                           balance=render_euros(user.balance))
                if not app.config['DEBUG']:
                    mail.send(msg)
                else:
                    print(u'Sending mail \n{}'.format(unicode(msg.as_string(),
                                                              'utf-8')))

            return redirect(url_for('admin'))
    else:
        return abort(403)


@app.route('/administrate/consumption/list', methods=['POST', 'GET'])
@login_required
def administrate_consumtion_list():
    if is_admin(g.user.username):
        form = ConsumptionListForm()
        if request.method == 'POST':
            if form.validate_on_submit():
                ids = form.uids.data
                units = form.units.data
                prices = form.prices.data
                print(ids, units, prices)
        else:
            return render_template('consumption_list.html', form=form)
    else:
        return abort(403)


@app.route("/administrate/expenses", methods=['POST'])
@login_required
def administrate_expenses():
    if is_admin(g.user.username):
        eform = ExpenseForm()
        if eform.validate_on_submit():
            description = eform.description.data
            amount = eform.amount.data
            date = (eform.date.data
                    if eform.date.data != ''
                    else datetime.utcnow())
            bc = BudgetChange(amount=amount,
                              description=description,
                              date=date)
            db.session.add(bc)
            db.session.commit()
        else:
            for field, errors in eform.errors.items():
                for error in errors:
                    flash(u'Error in the %s field - %s'
                          % (getattr(eform, field).label.text, error))

        return redirect(url_for('admin'))
    else:
        return abort(403)


@app.route('/administrate/service.pdf')
@login_required
def administrate_service_list():
    services = db.session.query(Service).all()
    string = render_template('service.tex', services=services)
    with codecs.open('build/service.tex', 'w', 'utf-8') as f:
        f.write(string)
    p = Popen(
        '/Library/Tex/texbin/lualatex --interaction=batchmode'
        ' --output-directory=build build/service.tex',
        shell=True
    )
    p.wait()
    return send_from_directory('build', 'service.pdf')


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))


def render_euros(num):
    minus = ""
    if num < 0:
        num *= -1
        minus = "-"

    euros = num // 100
    cents = num % 100
    return (u'{}{}.{:02d} €'.format(minus, euros, cents))


@app.template_filter()
@evalcontextfilter
def euros(eval_ctx, value):
    return render_euros(value)


def ldap_get(username):
    ldap_server = app.config['LDAP_HOST']
    base_dn = app.config['LDAP_SEARCH_BASE']
    connect = ldap.open(ldap_server, port=app.config['LDAP_PORT'])
    try:
        connect.bind_s('', '')
        result = connect.search_s(base_dn, ldap.SCOPE_SUBTREE,
                                  'uid={}'.format(username))
        connect.unbind_s()
        if result:
            data = result[0][1]
            return data
        else:
            return None
    except ldap.LDAPError, e:
        print('LDAP error: {}'.format(e))
        connect.unbind_s()
        return None


def ldap_authenticate(username, password):
    print('Trying to authenticate {}'.format(username))
    ldap_server = app.config['LDAP_HOST']
    base_dn = app.config['LDAP_SEARCH_BASE']
    connect = ldap.open(ldap_server, port=app.config['LDAP_PORT'])
    search_filter = "uid=" + username
    try:
        connect.bind_s('uid=' + username + ',' + base_dn, password)
        result = connect.search_s(base_dn, ldap.SCOPE_SUBTREE, search_filter)
        connect.unbind_s()
        data = result[0][1]
        return data
    except ldap.LDAPError, e:
        print('LDAP error: {}'.format(e))
        connect.unbind_s()
        return None


login_manager.login_view = 'login'

if __name__ == '__main__':
    app.run(host='localhost', port=5001)
