import unittest

from core import db, app
from core.control import LOGIN_PATH
from core.models import User
from core.views import BAD_FORMAT_MESSAGE, BAD_TOKEN_MESSAGE, INVALID_TOKEN_MESSAGE, TOKEN_EXPIRED_MESSAGE, \
    LOGIN_MESSAGE


class TestFlaskAPIs(unittest.TestCase):

    def create_app(self):
        app.config.from_object('src.core.config.TestingConfig')
        return app

    def init_db(self):
        self.expired_token = ('eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.'
                              'eyJleHAiOjE1MjA2OTI5MzEsImlhdCI6MTUxODEwMDkzMSwic3ViIjoxfQ.'
                              '4uuIsAIpxng-dcPQxXQvN3vjibxxeJpQFcaqBw0z4Eg')

        thing1 = User(name='thing1')
        thing1.id = 1
        thing1.token = self.expired_token

        thing2 = User(name='thing2')
        thing2.id = 2
        thing2.token = self.valid_token = thing2.encode_auth_token(thing2.id).decode('utf-8')

        db.session.add(thing1)
        db.session.add(thing2)
        db.session.commit()

    def setUp(self):
        self.app = self.create_app()
        self.app.testing = True
        self.client = app.test_client()
        with self.app.app_context():
            db.create_all()
        self.init_db()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_login_bad_format_request(self):
        rv = self.client.post(LOGIN_PATH)
        assert str.encode(BAD_FORMAT_MESSAGE) in rv.data

    def test_login_without_token(self):
        rv = self.client.post(LOGIN_PATH, data='{"key":"value"}')
        assert str.encode(BAD_TOKEN_MESSAGE) in rv.data

    def test_login_with_invalid_token(self):
        rv = self.client.post(LOGIN_PATH, data='{"token":"invalid"}')
        assert str.encode(INVALID_TOKEN_MESSAGE) in rv.data

    def test_login_with_expired_token(self):
        rv = self.client.post(LOGIN_PATH, data='{"token":"' + self.expired_token + '"}')
        assert str.encode(TOKEN_EXPIRED_MESSAGE) in rv.data

    def test_login_with_valid_token(self):
        rv = self.client.post(LOGIN_PATH, data='{"token":"' + self.valid_token + '"}')
        assert str.encode(LOGIN_MESSAGE) in rv.data


if __name__ == '__main__':
    unittest.main()
