import coffee
import unittest
from mongoengine import connect
from database import User

class CoffeeTestCase(unittest.TestCase):
    def setUp(self):
        coffee.app.config['TESTING'] = True
        coffee.app.config['DB_NAME'] = coffee.app.config['DB_NAME'] + '-test'
        self.app = coffee.app.test_client()
        with coffee.app.app_context():
            db = connect(coffee.app.config['DB_NAME'],
                         host=coffee.app.config['DB_HOST'],
                         port=coffee.app.config['DB_PORT'])

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

if __name__ == '__main__':
    unittest.main()
