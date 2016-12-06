# coding: utf-8

from __future__ import division, unicode_literals

from datetime import datetime, timedelta
from ldap3 import Server, Connection
from wtforms import (StringField,
                     PasswordField,
                     BooleanField,
                     IntegerField,
                     DecimalField,
                     HiddenField,
                     FieldList,
                     FormField,
                     SelectField,
                     validators,
                     TextField)
from wtforms import Form as NoCsrfForm
from wtforms.fields.html5 import DateField

from jinja2 import evalcontextfilter

from flask import (Flask,
                   render_template,
                   redirect,
                   g,
                   url_for,
                   request,
                   send_from_directory,
                   flash,
                   jsonify,
                   Blueprint,
                   abort)
from flask_login import (LoginManager,
                         login_user,
                         logout_user,
                         current_user,
                         login_required)
from flask_wtf import FlaskForm
from flask_mail import Mail, Message
from flask_admin import Admin
from flask_admin.contrib.peewee import ModelView
from peewee import fn

import codecs

from subprocess import Popen

from math import exp

from database import User, Transaction, Service, Consumption, db

app = Flask(__name__)
app.config.from_object('config')
app.config.from_envvar('COFFEE_SETTINGS', silent=True)

bp = Blueprint('coffee', __name__, template_folder='templates', static_folder='static')

login_manager = LoginManager(app)
login_manager.login_view = 'coffee.login'
login_manager.blueprint_login_views = {
    'coffee': 'coffee.login',
}

mail = Mail()
mail.init_app(app)

admin = Admin(app, name='E5 MoCA DB ADMIN', template_mode='bootstrap3', url=app.config['BASEURL'] + '/admin/db')
admin.add_view(ModelView(User))
admin.add_view(ModelView(Transaction))
admin.add_view(ModelView(Service))


class LoginForm(FlaskForm):
    username = StringField('Username')
    password = PasswordField('Password')
    remember = BooleanField('remember', default=False)


class FlexibleDecimalField(DecimalField):
    def process_formdata(self, valuelist):
        if valuelist:
            valuelist[0] = valuelist[0].replace(',', '.')
        return super(FlexibleDecimalField, self).process_formdata(valuelist)


class PaymentForm(FlaskForm):
    uid = SelectField('Name', choices=[], coerce=int)
    amount = FlexibleDecimalField('Amount')


class ConsumptionForm(FlaskForm):
    uid = SelectField('Name', choices=[], coerce=int)
    units = FieldList(IntegerField('Units', [validators.optional()]))


class ExpenseForm(FlaskForm):
    description = TextField('Description')
    amount = FlexibleDecimalField('Amount')
    date = DateField('Date', default=datetime.utcnow)


@app.teardown_request
def after_request(callback):
    if not db.is_closed():
        db.close()


@login_manager.user_loader
def load_user(username):
    if app.config['DEBUG'] and not app.config['USE_LDAP']:
        return User.get_or_create(username=username, defaults={
            'name': username,
            'admin': True,
        })[0]
    return User.get(User.username == username)


@app.template_filter('euros')
def euros(amount):
    return '{:.2f}€'.format(amount / 100)


def is_admin():
    return current_user.admin or app.config['DEBUG']


@bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    coffee_prices = app.config['COFFEE_PRICES']
    target_budget = (
        Consumption
        .select(fn.SUM(Consumption.units * Consumption.price_per_unit))
        .scalar() +
        Transaction
        .select(fn.SUM(Transaction.diff))
        .where(Transaction.user == None)  # noqa
        .scalar())
    actual_budget = Transaction.select(fn.SUM(Transaction.diff)).scalar()

    return render_template(
        "global.html", current_budget=actual_budget,
        target_budget=target_budget,
        coffee_prices=coffee_prices
    )


@bp.route('/personal/')
@login_required
def personal():
    user = User.get(User.username == current_user.username)
    balance = user.balance
    if balance > 0:
        balance_type = 'positive'
    else:
        balance_type = 'negative'
    return render_template('personal.html', user=user, balance=balance,
                           balance_type=balance_type)


@bp.route('/personal_data.json')
@login_required
def personal_data():
    data = []

    user = User.get(User.id == current_user.id)
    for t in user.transactions:
        data.append((t.date.date(), t.diff))

    # calculate consumption every friday
    weekly = 0
    current_date = datetime.today().date()
    last_total = current_date
    for c in user.consumptions.order_by(Consumption.date.desc()):
        current_date = c.date.date()
        weekly -= c.units * c.price_per_unit
        if current_date < last_total:
            data.append((last_total, weekly))
            weekly = 0
            # use the last friday to calculate total consumption for one week
            last_total = current_date - timedelta(days=current_date.weekday() + 3)

    result = []
    for (d, a) in sorted(data, key=lambda x: x[0], reverse=True):
        result.append({'date': str(d), 'amount': a})

    return jsonify(data=result)


@bp.route('/global_data.json')
@login_required
def global_data():
    changes = Transaction.select()
    li = []
    for c in changes:
        li.append((str(c.date.date()), c.diff, c.description))
    result = []
    for l in sorted(li, key=lambda x: x[0]):
        result.append({'date': l[0], 'amount': l[1], 'description': l[2]})
    return jsonify(data=result)


def ldap_login(username, password, remember=False):
    if app.config['DEBUG'] and not app.config['USE_LDAP']:
        user, created = User.get_or_create(username=username,
                                           defaults=dict(name=username))
        print(user, user.is_authenticated, created)
        login_user(user, remember=remember)
        return True

    data = ldap_authenticate(username, password)
    if data:
        user, created = User.get_or_create(username=username)
        user.name = data[0]['cn']
        try:
            user.email = data[0]['mail']
        except KeyError:
            print('A user has no mail entry in LDAP!')
        user.save()
        login_user(user, remember=remember)
        return True
    else:
        return False


@bp.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        remember = form.remember.data
        if not ldap_login(username, password, remember=remember):
            return '<h1>Login failed</h1>'
        return redirect(url_for('coffee.index'))
    return render_template('login.html', form=form)


def get_listofshame():
    entries = []
    for u in User.select():
        entries.append({'name': u.name,
                        'balance': u.balance,
                        'active': u.active,
                        'score': u.score})
    li = sorted(entries, key=lambda e: (-e['active'], e['balance']))
    return li


@bp.route('/admin/')
@login_required
def admin():
    if not is_admin():
        return abort(403)

    pform = PaymentForm()
    pform.uid.choices = User.get_uids()
    cform = ConsumptionForm()
    cform.uid.choices = User.get_uids()
    for price, title in app.config['COFFEE_PRICES']:
        cform.units.append_entry()
        cform.units[-1].label = title
    eform = ExpenseForm()
    listofshame = get_listofshame()
    return render_template('admin.html', payment_form=pform,
                           consumption_form=cform, expense_form=eform,
                           listofshame=listofshame)


@bp.route("/admin/payment/", methods=['POST'])
@login_required
def submit_payment():
    if not is_admin():
        return abort(403)

    pform = PaymentForm()
    pform.uid.choices = User.get_uids()
    if not pform.validate_on_submit():
        flash('Payment invalid.')
        return redirect(url_for('coffee.admin'))

    uid = pform.uid.data
    amount = float(pform.amount.data) * 100
    user = User.get(User.id == uid)
    transaction = Transaction(user=user, diff=amount,
                              description='{} payment from {}'
                              .format(euros(amount), user.name))
    transaction.save()
    if user.email:
        msg = Message('[Kaffeeministerium] Einzahlung von {}'
                      .format(euros(amount)))
        msg.charset = 'utf-8'
        msg.add_recipient(user.email)
        msg.body = render_template('mail/payment',
                                   amount=amount,
                                   balance=user.balance)
        flash('Mail sent to user {}'.format(user.name))
        if not app.config['DEBUG']:
            mail.send(msg)
        else:
            print(u'Sending mail \n{}'.format(msg.as_string()))

    return redirect(url_for('coffee.admin'))


@bp.route("/administrate/consumption", methods=['POST'])
@login_required
def administrate_consumption():
    if not is_admin():
        return abort(403)

    cform = ConsumptionForm()
    cform.uid.choices = User.get_uids()
    if not cform.validate_on_submit():
        return 'Form not valid'

    uid = cform.uid.data
    user = User.get(User.id == uid)
    user.active = True
    user.save()

    # Check if there was any useful input
    if True not in [x and x > 0 for x in cform.units.data]:
        flash('No updates given.')
        return redirect(url_for('coffee.admin'))

    for u, c in zip(cform.units.data, app.config['COFFEE_PRICES']):
        if(u):
            consumption = Consumption(units=u, price_per_unit=c[0], user=user)
            consumption.save()
    balance = user.balance
    if balance < app.config['BUDGET_WARN_BELOW']:
        if user.email:
            msg = Message(u"[Kaffeeministerium] Geringes Guthaben!")
            msg.charset = 'utf-8'
            msg.add_recipient(user.email)
            msg.body = render_template('mail/lowbudget',
                                       balance=euros(balance))
            if not app.config['DEBUG']:
                mail.send(msg)
            else:
                print(u'Sending mail \n{}'.format(msg.as_string()))
            flash('Warning mail sent. Balance is {}'.format(euros(balance)))
        else:
            flash('Balance is {}. User could not be notified.'.format(euros(balance)))

    return redirect(url_for('coffee.admin'))


@bp.route("/app/", methods=['GET'])
def mobile_app():
    if request.args.get('jsdev'):
        code_url = 'http://localhost:8080/dev-bundle/app.js'
    else:
        code_url = url_for('coffee.static', filename='build/app.js')
    return render_template('app.html', code_url=code_url)


@bp.route("/app/api/<function>/", methods=['GET', 'POST'])
def api(function):

    def get_userlist():
        # always calculate user list
        today = datetime.now().replace(hour=0, minute=0)
        return [{'name': u.name,
                 'id': u.id,
                 'consume': (u.consumptions
                     .select(fn.SUM(Consumption.units))
                     .where(Consumption.date >= today)
                     .scalar() or 0)
                 } for u in User.select().where(User.active)]

    if function == 'user_list':
        return jsonify(users=get_userlist())

    if function == 'add_consumption':
        data = request.get_json()
        prices = {price[1]: price[0] for price in app.config['COFFEE_PRICES']}
        created = Consumption(user=data['id'],
                              price_per_unit=prices[data['consumption_type']],
                              units=data['cur_consumption'],
                              date=datetime.now()).save()
        return jsonify(status='success', users=get_userlist())


@bp.route("/administrate/expenses", methods=['POST'])
@login_required
def administrate_expenses():
    if not is_admin():
        return abort(403)

    eform = ExpenseForm()
    if not eform.validate_on_submit():
        for field, errors in eform.errors.items():
            for error in errors:
                flash(u'Error in the %s field - %s'
                      % (getattr(eform, field).label.text, error))
        return redirect(url_for('coffee.admin'))

    description = eform.description.data
    amount = eform.amount.data
    date = (eform.date.data
            if eform.date.data != ''
            else datetime.utcnow())
    t = Transaction(diff=100 * amount, date=date, description=description)
    t.save()
    flash('Transaction stored.')
    return redirect(url_for('coffee.admin'))


# @app.route('/admin/service.pdf')
# @login_required
# def administrate_service_list():
#     services = Service.select().order_by(Service.date.desc())[0:5]
#     services = list(reversed(services))
#     string = render_template('service.tex', services=services)
#     with codecs.open('build/service.tex', 'w', 'utf-8') as f:
#         f.write(string)
#     p = Popen(
#         '/Library/Tex/texbin/lualatex --interaction=batchmode'
#         ' --output-directory=build build/service.tex',
#         shell=True
#     )
#     p.wait()
#     return send_from_directory('build', 'service.pdf')
#
#
# @app.route('/administrate/service/update/')
# @login_required
# def administrate_service_update():
#     services = []
#     users = User.query.filter(User.active, User.vip == false()).all()
#     users = sorted(users, key=lambda x: x.score)
#     last_service = Service.query.order_by(Service.date.desc()).first()
#     last_date = last_service.date
#     for u in users[0:5]:
#         s = Service(
#             start=last_date + timedelta(3),
#             end=last_date + timedelta(7),
#         )
#         services.append(s)
#         u.services.append(s)
#         last_date += timedelta(7)
#     db.session.commit()
#     return 'Services Updated: {}'.format(
#         ['{}'.format(st.user.name) for st in services]
#     )


@bp.route('/admin/list.pdf')
@login_required
def administrate_list():
    users = []
    for u in User.select().where(User.active | User.vip).order_by(User.name):
        consumptions = sorted(u.consumptions, key=lambda x: x.date)
        if not u.vip and (consumptions and (
                datetime.utcnow() - consumptions[-1].date) > timedelta(90)):
            u.active = False
            u.save()
        else:
            users.append(u)
    string = render_template('list.tex',
                             current_date=datetime.utcnow(),
                             users=users,
                             vip=list(User.select(User.name).where(User.vip)))
    with codecs.open('build/list.tex', 'w', 'utf-8') as f:
        f.write(string)
    p = Popen(
        '/Library/Tex/texbin/lualatex --interaction=batchmode'
        ' --output-directory=build build/list.tex',
        shell=True
    )
    p.wait()
    return send_from_directory('build', 'list.pdf')


@bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('coffee.login'))


def ldap_authenticate(username, password):
    try:
        ldap_server = Server(app.config['LDAP_HOST'], port=app.config['LDAP_PORT'])
        base_dn = app.config['LDAP_SEARCH_BASE']
        ldap_conn = Connection(ldap_server,
                               "uid={},cn=users,{}".format(username, base_dn),
                               password)
        if ldap_conn.search(base_dn,
                            '(&(objectclass=person)(uid={}))'.format(username),
                            attributes=['mail', 'cn']):
            return ldap_conn.entries
    except:
        pass

    return None


login_manager.login_view = 'login'

app.register_blueprint(bp, url_prefix=app.config['BASEURL'])

if __name__ == '__main__':
    if db.is_closed():
        db.connect()
        db.create_tables([User, Transaction, Consumption, Service], safe=True)
    app.run(host=app.config['SERVER'], port=app.config['PORT'])
