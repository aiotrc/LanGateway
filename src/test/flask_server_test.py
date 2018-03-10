import os
import unittest
import tempfile

from core import app, db
from core.control import LOGIN_PATH
from core.models import User
from core.views import BAD_FORMAT_MESSAGE, BAD_TOKEN_MESSAGE, INVALID_TOKEN_MESSAGE, TOKEN_EXPIRED_MESSAGE
from manage import create_db


class TestFlaskAPIs(unittest.TestCase):

    def create_app(self):
        app.config.from_object('src.core.config.TestingConfig')
        return app

    def setUp(self):
        self.app = self.create_app()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_login_bad_format_request(self):
        rv = self.app.post(LOGIN_PATH)
        assert str.encode(BAD_FORMAT_MESSAGE) in rv.data

    def test_login_without_token(self):
        rv = self.app.post(LOGIN_PATH, data='{"key":"value"}')
        assert str.encode(BAD_TOKEN_MESSAGE) in rv.data

    def test_login_with_invalid_token(self):
        rv = self.app.post(LOGIN_PATH, data='{"token":"invalid"}')
        assert str.encode(INVALID_TOKEN_MESSAGE) in rv.data

    def test_login_with_expired_token(self):
        user = User(
            name='thing'
        )
        user.token = user.encode_auth_token(user.id)
        # insert the user
        db.session.add(user)
        db.session.commit()
        rv = self.app.post(LOGIN_PATH,
                           data='{"token":"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.\
                           eyJleHAiOjE1MjA2OTI5MzEsImlhdCI6MTUxODEwMDkzMSwic3ViIjoxfQ.\
                           4uuIsAIpxng-dcPQxXQvN3vjibxxeJpQFcaqBw0z4Eg"}')
        print(rv.data)
        assert str.encode(TOKEN_EXPIRED_MESSAGE) in rv.data


if __name__ == '__main__':
    unittest.main()
