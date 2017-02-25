import coffee
import unittest
from mongoengine import connect
from database import User, Transaction, Consumption
from flask import g

class CoffeeTestCase(unittest.TestCase):
    def setUp(self):
        coffee.app.config['TESTING'] = True
        coffee.app.config['DEBUG'] = True
        coffee.app.config['DB_NAME'] = 'coffeedb-test'
        coffee.app.config['WTF_CSRF_ENABLED'] = False
        self.app = coffee.app.test_client()
        db = connect(coffee.app.config['DB_NAME'],
                     host=coffee.app.config['DB_HOST'],
                     port=coffee.app.config['DB_PORT'])
        testuser = User(username='testuser', email='test@coffee.py')
        testuser.save()
        User(username='admin', email='admin@coffee.py', admin=True).save()
        testpayment = Transaction(diff=1000, user=testuser)
        testpayment.save()
        testexpense = Transaction(diff=-500)
        testexpense.save()
        testcons = Consumption(units=1, price_per_unit=50, user=testuser)
        testcons.save()

    def tearDown(self):
        db = connect(coffee.app.config['DB_NAME'],
                     host=coffee.app.config['DB_HOST'],
                     port=coffee.app.config['DB_PORT'])
        db.drop_database(coffee.app.config['DB_NAME'])

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

if __name__ == '__main__':
    unittest.main()
