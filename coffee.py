from functools import wraps

from datetime import datetime
import pendulum
from wtforms import (
    StringField,
    PasswordField,
    BooleanField,
    IntegerField,
    DecimalField,
    FieldList,
    SelectField,
    validators,
    DateField,
)

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
                   session,
                   abort)
from flask_login import (LoginManager,
                         login_user,
                         logout_user,
                         current_user,
                         login_required)
from flask_wtf import FlaskForm
from flask_admin import Admin
from flask_admin.contrib.mongoengine import ModelView
from flask_mongoengine import MongoEngine

import smtplib
from email.message import EmailMessage

from database import User, Transaction, Service, Consumption, AchievementDescriptions
from authentication import user_login
import achievements

app = Flask(__name__)
app.config.from_object('config')
app.config.from_envvar('COFFEE_SETTINGS', silent=True)
db = MongoEngine(app)

bp = Blueprint('coffee', __name__, template_folder='templates', static_folder='static')

login_manager = LoginManager(app)
login_manager.login_view = 'coffee.login'
login_manager.blueprint_login_views = {
    'coffee': 'coffee.login',
}


class AuthenticatedModelView(ModelView):
    can_set_page_size = True
    def is_accessible(self):
        return current_user.admin or app.config['DEBUG']


class UserView(AuthenticatedModelView):
    page_size = 1000
    column_searchable_list = ['username', 'name', 'email']
    column_filters = ['admin', 'active', 'vip']
    column_default_sort = 'username'
    column_editable_list = ['vip', 'active', 'admin', 'email', 'name']
    inline_models = ['service']
    form_subdocuments = {
        'achievements': {
            # weirdo None field like here
            # http://flask-admin.readthedocs.io/en/latest/api/mod_contrib_mongoengine/#flask_admin.contrib.mongoengine.ModelView.form_subdocuments
            'form_subdocuments': {
                None: {
                    'form_columns': None,
                    'form_widget_args': {
                        'title': {
                            'rows': 1
                            },
                        'key': {
                            'rows': 1
                            }
                        }
                    }
                }
            }
        }


class ConsumptionView(AuthenticatedModelView):
    page_size = 1000
    column_default_sort = 'date'
    column_list = ['date', 'user', 'units', 'price_per_unit']


class ServiceView(AuthenticatedModelView):
    column_editable_list = ['service_count', 'date', 'user']


admin = Admin(app, name='E5 MoCA DB ADMIN', template_mode='bootstrap3',
              url=app.config['BASEURL'] + '/admin/db')
admin.add_view(UserView(User))
admin.add_view(AuthenticatedModelView(Transaction))
admin.add_view(ServiceView(Service))
admin.add_view(ConsumptionView(Consumption))
admin.add_view(AuthenticatedModelView(AchievementDescriptions))


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
    description = StringField('Description')
    amount = FlexibleDecimalField('Amount')
    date = DateField('Date', default=datetime.utcnow)


class MailCredentialsForm(FlaskForm):
    mail_user = StringField('MailUser')
    password = PasswordField('Password')


def getMailServer():
    # dont even try if no username is given
    if not app.config['MAIL_USERNAME']:
        return

    # try to get the mail connection from the app context
    s = getattr(g, '_mailserver', None)

    # establish a new connection if none is available
    if s is None:
        try:
            s = smtplib.SMTP(app.config['MAIL_SERVER'], app.config['MAIL_PORT'])
            s.starttls()
            s.login(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
            g._mailserver = s
        except:
            flash(f'Could not connect to Mailserver {app.config["MAIL_SERVER"]}.')
            return
    else:
        # test the mail connection
        try:
            s.ehlo()
        except Exception as e:
            return

    return s


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
    docs = list(Consumption.objects.aggregate(
        {
            '$group': {
                '_id': 'total',
                'total': {'$sum': {'$multiply': ['$units', '$price_per_unit']}},
            }
        }
    ))
    total_consumptions = docs[0]['total'] if len(docs) else 0
    docs = list(Transaction.objects(user=None).aggregate(
        {
            '$group': {
                '_id': 'total',
                'total': {'$sum': '$diff'},
            }
        }
    ))
    total_expenses = docs[0]['total'] if len(docs) else 0
    target_budget = total_consumptions + total_expenses
    docs = list(Transaction.objects.aggregate(
        {
            '$group': {
                '_id': 'total',
                'total': {'$sum': '$diff'},
            }
        }
    ))
    actual_budget = docs[0]['total'] if len(docs) else 0

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


@bp.route('/global_api/<function>/', methods=['GET'])
@login_required
def global_api(function):
    if function == 'personal_data':
        user = User.objects.get(username=current_user.username)
        return jsonify(data=user.consumption_list())

    if function == 'global_data':
        # some renaming
        actual_curve = [
                dict(date=t['_id'], amount=t['total'])
                for t in Transaction.dailyTransactions()
                ]
        consumption_curve = Consumption.dailyConsumptions()

        expense_curve = Transaction.dailyExpenses()
        # get all unique dates
        unique_dates = set([t['_id'] for t in expense_curve]).union(
                set([t['_id'] for t in consumption_curve ]))
        target_curve = []
        for date in unique_dates:
            amount = (next((x['total'] for x in expense_curve if x['_id'] == date), 0)
                      + next((x['total'] for x in consumption_curve if x['_id'] == date), 0))
            target_curve.append(dict(date=date, amount=amount))
        target_curve = sorted(target_curve, key=lambda x: x['date'])
        return jsonify(actual_curve=actual_curve, target_curve=target_curve)

    if function == 'consumption_times':
        """ return a list of consumtion daytimes, in seconds """
        def getSecondsOfDay(dates):
            for d in dates:
                yield d.subtract(years=d.year-1970, months=d.month-1,
                                 days=d.day-1).timestamp()

        consumptions = Consumption.objects(date__gte=pendulum.now().subtract(days=28))
        consumptions4Weeks = [pendulum.instance(c.date) for c in consumptions]
        consumptions1Week = [c for c in consumptions4Weeks if pendulum.now().subtract(days=7) < c]
        return jsonify(last_four_weeks=list(getSecondsOfDay(consumptions4Weeks)),
                       last_week=list(getSecondsOfDay(consumptions1Week)))

    return abort(404)


def switch_to_user(username):
    user = User.objects.get(username=username)
    logout_user()
    login_user(user, remember=True, force=True)


@bp.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        remember = form.remember.data
        if not user_login(username, password, remember=remember):
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
def admin(foo=True):
    # append jsdev get argument if in debug mode
    if app.config['JSDEV'] and not 'jsdev' in request.args.keys():
        return redirect(url_for('coffee.admin', jsdev=True))
    pform = PaymentForm()
    pform.uid.choices = User.get_uids()
    cform = ConsumptionForm()
    cform.uid.choices = User.get_uids()
    for price, title in app.config['COFFEE_PRICES']:
        cform.units.append_entry()
        cform.units[-1].label = title
    eform = ExpenseForm()
    mail_form = MailCredentialsForm()

    # try to contact the mailserver and report a successful login
    mailServer = getMailServer()
    return render_template('admin.html', payment_form=pform,
                           consumption_form=cform, expense_form=eform,
                           mail_form=mail_form,
                           mail_username=app.config['MAIL_USERNAME'] or '',
                           code_url=js_url('admin'),
                           mail_status=mailServer is not None)


@bp.route('/admin/api/<function>/', methods=['GET', 'POST'])
@admin_required
def admin_api(function):
    def listofshame():
        return [{'name': u.name,
                 'balance': u.balance,
                 'score': u.score,
                 'id': str(u.id),
                 'switch_url': url_for('coffee.administrate_switch_user', username=u.username),
                 'vip': u.vip,
                 'last_service': getattr(u.last_service, 'date', None),
                 }
                 for u in User.objects(active=True)
               ]

    def next_service_periods():
        """ Return a list of date perios where no master service is defined
        """
        # get all upcoming services
        upcomingServices = list(Service.objects.aggregate(
            {'$match': {
                'date': {'$gte': pendulum.today()},
                'master': True,
                }},
            {'$group': {
                '_id': {
                    '$dateToString': {
                        # group by Year-Week
                        'format': '%Y%U', 'date': '$date'}
                    }
                }}))
        # also get upcoming 8 weeks if no service is set for this week
        upcoming_weeks = []
        nextMonday = pendulum.today().next(pendulum.MONDAY)
        for weekDelta in range(8):
            nextStartDate = nextMonday.add(weeks=weekDelta)
            if nextStartDate.format('%Y%U') not in [s['_id'] for s in upcomingServices]:
                nextEndDate = nextStartDate.next(pendulum.FRIDAY)
                upcoming_weeks.append(f'{nextStartDate.to_date_string()}:{nextEndDate.to_date_string()}')
        return upcoming_weeks

    if function == 'listofshame':
        return jsonify(list=listofshame(), nextServicePeriods=next_service_periods())

    if function == 'add_service':
        data = request.get_json()
        user = User.objects.get(id=data.get('uid'))
        start, end = [pendulum.parse(d) for d in data.get('interval').split(':')]
        for day in pendulum.period(start, end):
            Service(user=user, date=day).save()
        return jsonify(list=listofshame(), nextServicePeriods=next_service_periods())

    return abort(404)


@bp.route("/admin/payment/", methods=['POST'])
@admin_required
def submit_payment():
    pform = PaymentForm()
    pform.uid.choices = User.get_uids()
    if not pform.validate_on_submit():
        flash('Payment invalid.')
        return redirect(url_for('coffee.admin'))

    uid = pform.uid.data
    # prevent inaccurate input parsing (see
    # https://docs.python.org/3.6/tutorial/floatingpoint.html)
    amount = int(round(float(pform.amount.data) * 100))
    user = User.objects.get(id=uid)
    transaction = Transaction(user=user, diff=amount,
                              description='{} payment from {}'
                              .format(euros(amount), user.name))
    transaction.save()
    if user.email:
        msg = EmailMessage()
        msg['Subject'] = f'[Kaffeeministerium] Einzahlung von {euros(amount)}'
        msg['From'] = app.config['MAIL_DEFAULT_SENDER']
        msg['To'] = user.email
        msg.set_content(render_template(
            'mail/payment', amount=amount, balance=user.balance,
            minister_name=app.config['MAIL_MINISTER_NAME']))
        flash('Mail sent to user {}'.format(user.name))
        if not app.config['DEBUG']:
            s = getMailServer()
            s.send_message(msg)
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
        if getMailServer() is not None:
            flash('Mail credentials updated')
        else:
            flash('Mail connection could not be established.')

    return redirect(url_for('coffee.admin'))


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
            msg = EmailMessage()
            msg['Subject'] = f'[Kaffeeministerium] Geringes Guthaben!'
            msg['From'] = app.config['MAIL_DEFAULT_SENDER']
            msg['To'] = user.email
            msg.set_content(render_template('mail/lowbudget',
                balance=euros(balance), minister_name=app.config['MAIL_MINISTER_NAME']))
            if not app.config['DEBUG']:
                s = getMailServer()
                s.send_message(msg)
            else:
                print(u'Sending mail \n{}'.format(msg.as_string()))
            flash('Warning mail sent. Balance is {}'.format(euros(balance)))
        else:
            flash(f'Balance is {euros(balance)}. User {user.name} could not be'
                  ' notified, no mail address available.')

    return redirect(url_for('coffee.admin'))


@bp.route("/app/", methods=['GET'])
@guest_required
def mobile_app():
    # append jsdev get argument if in debug mode
    if app.config['JSDEV'] and not 'jsdev' in request.args.keys():
        return redirect(url_for('coffee.mobile_app', jsdev=True))
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
            # build user dictionary manually
            user_dict = {
                'name': user.name,
                'username': user.username,
                'id': str(user.id),
                'consume': [],
                # fill in all of todays achievements
                'achievements': [{
                    'key': a.key,
                    'date': a.date,
                    }
                    for a in user.achievements
                    if a.date > pendulum.today()]
            }
            # perform a query for todays consumptions for each user
            # @TODO: try to move this to the mongo query... instead of hitting
            # the DB n + 1 times.
            for consume in Consumption.objects(user=user, date__gte=today):
                if consume.price_per_unit in prices:
                    user_dict['consume'].extend(
                        consume.units * [prices.get(consume.price_per_unit)]
                    )
            users.append(user_dict)
        return users

    def get_service():
        current_service = Service.current()
        last_cleaned = (
                Service
                .objects(master=True, cleaned=True)
                .order_by('-date')
                .first()
                )
        service = {
            'uid': str(current_service.user.id),
            'last_cleaned': last_cleaned.date if last_cleaned else 'Never',
            'upcoming': [dict(week=s['_id'], user=str(s['user'])) for s in Service.upcoming()]
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
    # prevent inaccurate input parsing (see
    # https://docs.python.org/3.6/tutorial/floatingpoint.html)
    amount = int(round(float(eform.amount.data * 100)))
    date = (eform.date.data
            if eform.date.data != ''
            else datetime.utcnow())
    t = Transaction(diff=amount, date=date, description=description)
    t.save()
    flash('Transaction stored.')
    return redirect(url_for('coffee.admin'))


@bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('coffee.login'))


login_manager.login_view = 'login'

app.register_blueprint(bp, url_prefix=app.config['BASEURL'])

if __name__ == '__main__':
    app.run(host=app.config['SERVER'], port=app.config['PORT'])
