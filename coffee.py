from functools import wraps

from datetime import datetime, timedelta
import pendulum
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
from flask_admin.contrib.mongoengine import ModelView

from database import User, Transaction, Service, Consumption

app = Flask(__name__)
app.config.from_object('config')
app.config.from_envvar('COFFEE_SETTINGS', silent=True)

bp = Blueprint('coffee', __name__, template_folder='templates', static_folder='static')

login_manager = LoginManager(app)
login_manager.login_view = 'coffee.login'
login_manager.blueprint_login_views = {
    'coffee': 'coffee.login',
}

mail = Mail(app)


class AuthenticatedModelView(ModelView):
    def is_accessible(self):
        try:
            return current_user.admin
        except:
            return False


admin = Admin(app, name='E5 MoCA DB ADMIN', template_mode='bootstrap3',
              url=app.config['BASEURL'] + '/admin/db')

admin.add_view(AuthenticatedModelView(User))
admin.add_view(AuthenticatedModelView(Transaction))
admin.add_view(AuthenticatedModelView(Service))
admin.add_view(AuthenticatedModelView(Consumption))


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
    uid = SelectField('Name', choices=[], coerce=str)
    amount = FlexibleDecimalField('Amount')


class ConsumptionForm(FlaskForm):
    uid = SelectField('Name', choices=[], coerce=str)
    units = FieldList(IntegerField('Units', [validators.optional()]))


class ExpenseForm(FlaskForm):
    description = TextField('Description')
    amount = FlexibleDecimalField('Amount')
    date = DateField('Date', default=datetime.utcnow)


class MailCredentialsForm(FlaskForm):
    mail_user = TextField('MailUser')
    password = PasswordField('Password')


def guest_required(f):
    @login_required
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if app.config['DEBUG'] or current_user.username == 'guest':
            return f(*args, **kwargs)
        else:
            abort(403)
    return decorated_function


def admin_required(f):
    @login_required
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if app.config['DEBUG'] or current_user.admin:
            return f(*args, **kwargs)
        else:
            abort(403)
    return decorated_function


@login_manager.user_loader
def load_user(username):
    try:
        user = User.objects.get(username=username)
    except:
        user = User(username=username, name=username)
    if app.config['DEBUG'] and not app.config['USE_LDAP']:
        user.admin = True
    return user


@app.template_filter('euros')
def euros(amount):
    return '{:.2f}€'.format(amount / 100)


@bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    coffee_prices = app.config['COFFEE_PRICES']
    total_consumptions = list(Consumption.objects.aggregate(
        {
            '$group': {
                '_id': 'total',
                'total': {'$sum': {'$multiply': ['$units', '$price_per_unit']}},
            }
        }
    ))[0]['total']
    total_expenses = list(Transaction.objects(user=None).aggregate(
        {
            '$group': {
                '_id': 'total',
                'total': {'$sum': '$diff'},
            }
        }
    ))[0]['total']
    target_budget = total_consumptions + total_expenses
    actual_budget = list(Transaction.objects.aggregate(
        {
            '$group': {
                '_id': 'total',
                'total': {'$sum': '$diff'},
            }
        }
    ))[0]['total']

    return render_template(
        "global.html", current_budget=actual_budget,
        target_budget=target_budget,
        coffee_prices=coffee_prices
    )


@bp.route('/personal/')
@login_required
def personal():
    user = User.objects.get(username=current_user.username)
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

    user = User.objects.get(username=current_user.username)
    for t in Transaction.objects(user=user):
        data.append((t.date.date(), t.diff))

    consumptions = list(Consumption.objects(user=user).order_by('-date'))
    if len(consumptions):
        # calculate consumption every friday
        weekly = 0
        last_total = consumptions[0].date.date()
        for c in consumptions:
            current_date = c.date.date()
            weekly -= c.units * c.price_per_unit
            if current_date <= last_total:
                data.append((last_total, weekly))
                weekly = 0
                # use the last friday to calculate total consumption for one week
                last_total = current_date - timedelta(days=current_date.weekday() + 3)

    result = []
    for (d, a) in sorted(data, key=lambda x: x[0]):
        result.append({'date': str(d), 'amount': a})

    return jsonify(data=result)


@bp.route('/global_data.json')
@login_required
def global_data():
    li = [dict(date=str(t.date.date()), amount=t.diff)
          for t in Transaction.objects.only('date', 'diff').order_by('date')]
    return jsonify(data=li)


def switch_to_user(username):
    user = User.objects.get(username=username)
    logout_user()
    login_user(user, remember=True, force=True)


def ldap_login(username, password, remember=False):
    if app.config['DEBUG'] and not app.config['USE_LDAP']:
        try:
            user = User.objects.get(username=username)
            user.admin = True
        except:
            user = User(username=username, name=username, admin=True,
                        active=True, email='dev@coffee.dev').save()
            warning = 'User did not exist, admin user created.'
            flash(warning)
        login_user(user, remember=remember)
        return True

    data = ldap_authenticate(username, password)
    if data:
        try:
            user = User.objects.get(username=username)
        except:
            user = User(username=username)
        user.name = str(data[0]['cn'])
        try:
            user.email = str(data[0]['mail'])
        except KeyError:
            print('A user has no mail entry in LDAP!')
        user.active = True
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


def js_url(script):
    if request.args.get('jsdev'):
        return 'http://localhost:8080/dev-bundle/%s.bundle.js' % script
    else:
        return url_for('coffee.static', filename='build/%s.bundle.js' % script)


@bp.route('/admin/')
@admin_required
def admin():
    pform = PaymentForm()
    pform.uid.choices = User.get_uids()
    cform = ConsumptionForm()
    cform.uid.choices = User.get_uids()
    for price, title in app.config['COFFEE_PRICES']:
        cform.units.append_entry()
        cform.units[-1].label = title
    eform = ExpenseForm()
    mail_form = MailCredentialsForm()
    return render_template('admin.html', payment_form=pform,
                           consumption_form=cform, expense_form=eform,
                           mail_form=mail_form,
                           mail_username=app.config['MAIL_USERNAME'] or '',
                           code_url=js_url('admin'))


@bp.route('/admin/api/<function>/', methods=['GET', 'POST'])
@admin_required
def admin_api(function):
    def listofshame():
        return [{'name': u.name,
                 'balance': u.balance,
                 'score': u.score,
                 'id': str(u.id),
                 'switch_url': url_for('coffee.administrate_switch_user', username=u.username),
                 'vip': u.vip
                 }
                 for u in User.objects(active=True)
               ]

    def next_service_periods():
        latest_service = pendulum.from_timestamp(Service.objects.order_by('-date')
                                                 .first().date.timestamp())
        periods = []
        for _ in range(8):
            nmo = latest_service.next(pendulum.MONDAY)
            nfr = nmo.next(pendulum.FRIDAY)
            periods.append('%s:%s' %(nmo.to_date_string(), nfr.to_date_string()))
            latest_service = nfr
        return periods

    if function == 'listofshame':
        return jsonify(list=listofshame(), nextServicePeriods=next_service_periods())

    if function == 'add_service':
        data = request.get_json()
        user = User.objects.get(id=data.get('uid'))
        start, end = [pendulum.parse(d) for d in data.get('interval').split(':')]
        for day in pendulum.period(start, end):
            Service(user=user, date=day).save()
        return jsonify(list=listofshame(), nextServicePeriods=next_service_periods())


@bp.route("/admin/payment/", methods=['POST'])
@admin_required
def submit_payment():
    pform = PaymentForm()
    pform.uid.choices = User.get_uids()
    if not pform.validate_on_submit():
        flash('Payment invalid.')
        return redirect(url_for('coffee.admin'))

    uid = pform.uid.data
    amount = float(pform.amount.data) * 100
    user = User.objects.get(id=uid)
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


@bp.route("/admin/switch-to-user/<username>/")
@admin_required
def administrate_switch_user(username):
    switch_to_user(username)
    if username == 'guest':
        return redirect(url_for('coffee.mobile_app'))
    else:
        return redirect(url_for('coffee.personal'))


@bp.route("/admin/mail-credentials/", methods=['POST'])
@admin_required
def administrate_mail_credentials():
    mform = MailCredentialsForm()
    if not mform.validate_on_submit():
        flash('Mail credentials invalid')
    else:
        app.config['MAIL_USERNAME'] = mform.mail_user.data
        app.config['MAIL_PASSWORD'] = mform.password.data
        mail.init_app(app)
        flash('Mail credentials updated')
    return redirect(url_for('coffee.admin'))


def warning_mail(user):
    msg = Message(u"[Kaffeeministerium] Geringes Guthaben!")
    msg.charset = 'utf-8'
    msg.add_recipient(user.email)
    msg.body = render_template('mail/lowbudget',
                               balance=euros(user.balance))
    if not app.config['DEBUG']:
        mail.send(msg)
    else:
        print(u'Sending mail \n{}'.format(unicode(msg.as_string(), 'utf-8')))


@bp.route("/administrate/consumption", methods=['POST'])
@admin_required
def administrate_consumption():
    cform = ConsumptionForm()
    cform.uid.choices = User.get_uids()
    if not cform.validate_on_submit():
        return 'Form not valid'

    uid = cform.uid.data
    user = User.objects.get(id=uid)
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
    flash('Consumptions for user %s added.' % user)
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
@guest_required
def mobile_app():
    return render_template('app.html', code_url=js_url('app'))


@bp.route("/app/api/<function>/", methods=['GET', 'POST'])
@guest_required
def api(function):
    prices = {p[0]: p[1] for p in app.config['COFFEE_PRICES']}
    products = {p[1]: p[0] for p in app.config['COFFEE_PRICES']}

    def get_userlist():
        # always calculate user list
        today = pendulum.today(app.config['TZ'])
        users = []
        for user in User.objects(active=True).order_by('-vip', 'name'):
            user_dict = {
                'name': user.name,
                'username': user.username,
                'id': str(user.id),
                'consume': []
            }
            for consume in Consumption.objects(user=user, date__gte=today):
                if consume.price_per_unit in prices:
                    user_dict['consume'].extend(
                        consume.units * [prices.get(consume.price_per_unit)]
                    )
            users.append(user_dict)
        return users

    def get_service():
        current_service = Service.current()
        service = {
            'uid': str(current_service.user.id),
            'cleaned': current_service.cleaned,
            'cleaningProgram': current_service.cleaning_program,
            'decalcifyProgram': current_service.decalcify_program,
        } if current_service else None
        return service

    if function == 'user_list':
        return jsonify(users=get_userlist(), service=get_service())

    if function == 'add_consumption':
        data = request.get_json()
        user = User.objects.get(id=data.get('id'))
        created = Consumption(user=user,
                              price_per_unit=products.get(data['consumption_type']),
                              units=data['cur_consumption'],
                              date=datetime.now()).save()
        if user.balance < app.config['BUDGET_WARN_BELOW']:
            alert = {
                'text': 'Geringes Guthaben, bitte laden Sie bald wieder auf.',
                'type': 'warning',
            }
        else:
            alert = None
        status = 'success' if created else 'failure'
        return jsonify(status=status, users=get_userlist(), alert=alert)

    if function == 'finish_service':
        data = request.get_json()
        service = Service.current()
        service.__setattr__(data.get('service'), True)
        service.save()
        return jsonify(service=get_service(), alert={'text': 'Service eingetragen', 'type': 'success'})

    return abort(404)


@bp.route("/administrate/expenses", methods=['POST'])
@admin_required
def administrate_expenses():
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


@bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('coffee.login'))


def ldap_authenticate(username, password):
    # the guest user is special
    assert(username != 'guest')
    try:
        ldap_server = Server(app.config['LDAP_HOST'], port=app.config['LDAP_PORT'])
        base_dn = app.config['LDAP_SEARCH_BASE']
        ldap_conn = Connection(ldap_server,
                               "uid={},{}".format(username, base_dn),
                               password,
                               auto_bind=True)
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
    app.run(host=app.config['SERVER'], port=app.config['PORT'])
