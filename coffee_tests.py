import coffee
import unittest
from mongoengine import connect
from database import User, Transaction, Consumption
from flask import g

class CoffeeTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        coffee.app.config['TESTING'] = True
        coffee.app.config['DB_NAME'] = 'coffeedb-test'
        coffee.app.config['WTF_CSRF_ENABLED'] = False
        db = connect(coffee.app.config['DB_NAME'],
                     host=coffee.app.config['DB_HOST'],
                     port=coffee.app.config['DB_PORT'])

    @classmethod
    def tearDownClass(cls):
        db = connect(coffee.app.config['DB_NAME'],
                     host=coffee.app.config['DB_HOST'],
                     port=coffee.app.config['DB_PORT'])
        db.drop_database(coffee.app.config['DB_NAME'])

    def setUp(self):
        testuser = User(username='testuser', email='test@coffee.py')
        testuser.save()
        self.testuser = testuser
        User(username='admin', email='admin@coffee.py', admin=True).save()
        testpayment = Transaction(diff=1000, user=testuser)
        testpayment.save()
        testexpense = Transaction(diff=-500)
        testexpense.save()
        testcons = Consumption(units=1, price_per_unit=50, user=testuser)
        testcons.save()
        self.app = coffee.app.test_client()

    def tearDown(self):
        User.drop_collection()
        Transaction.drop_collection()
        Consumption.drop_collection()

    def test_index_redirect(self):
        rv = self.app.get('/')
        assert(b'Redirecting...' in rv.data)

    def test_login_at_index(self):
        rv = self.app.get('/', follow_redirects=True)
        assert(b'LDAP Login' in rv.data)

    def login(self, username, password):
        return self.app.post('/login',
                             data=dict(
                                 username=username,
                                 password=password,
                                 remember='y',
                                 ),
                             follow_redirects=True,
                             )

    def logout(self):
        return self.app.get('/logout', follow_redirects=True)

    def test_login_logout(self):
        rv = self.login('testuser', 'foobar')
        assert(b'Actual Budget' in rv.data)
        rv = self.logout()
        assert(b'LDAP Login' in rv.data)
        rv = self.login('testuser', 'foobar-wrong')
        assert(b'Login failed' in rv.data)

    def test_login_new_user(self):
        rv = self.login('newuser', 'foobar')
        assert(b'Actual Budget' in rv.data)

    def test_guest_login(self):
        rv = self.login('guest', 'pw')
        assert(b'Login failed' in rv.data)

    def test_admin_access(self):
        rv = self.login('admin', 'foobar')
        assert(b'Actual Budget' in rv.data)
        rv = self.app.get('/admin/')
        assert(b'Adminpanel' in rv.data)

    def test_admin_access_unauthorized(self):
        rv = self.login('testuser', 'foobar')
        assert(b'Actual Budget' in rv.data)
        rv = self.app.get('/admin/')
        assert(rv.status_code == 403)

    def test_admin_access_db(self):
        rv = self.login('admin', 'foobar')
        assert(rv.status_code == 200)
        assert(b'Actual Budget' in rv.data)
        rv = self.app.get('/admin/db/consumption/')
        assert(rv.status_code == 200)

    def test_admin_access_db_unauthorized(self):
        rv = self.login('testuser', 'foobar')
        assert(rv.status_code == 200)
        assert(b'Actual Budget' in rv.data)
        rv = self.app.get('/admin/db/consumption/')
        assert(rv.status_code == 403)

    def test_consumption_list(self):
        consumption_list = self.testuser.consumption_list()
        assert(len(consumption_list) == 2)
        assert(consumption_list[0]['amount'] == -50)
        assert(consumption_list[1]['amount'] == 1000)

    def test_last_service(self):
        assert(self.testuser.last_service is None)

if __name__ == '__main__':
    unittest.main()
