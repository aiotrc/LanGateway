import random
import unittest
from unittest import mock

import flask_login
from flask_login import UserMixin

from core import app, db
from core.models import User
from core.socketio_runner import DATA_RESPONSE_TOPIC, DATA_TOPIC, COMMAND_TOPIC, socketio


class TestClient(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = cls.create_app()
        cls.client = socketio.test_client(app=cls.app)
        cls.client.testing = True

        cls.http_client = cls.app.test_client()

        thing = User(name='thing')
        cls.valid_token = thing.encode_auth_token(1).decode('utf-8')

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        db.drop_all()
        with self.app.app_context():
            db.create_all()

        self.init_db()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    @staticmethod
    def create_app():
        app.config.from_object('src.core.config.TestingConfig')
        return app

    def init_db(self):
        thing1 = User(name='thing1')
        thing1.id = 1

        db.session.add(thing1)
        db.session.commit()

    def test_handle_data_without_login(self):
        self.client.emit(DATA_TOPIC, {'data': random.randint(10, 100)})

        received = self.client.get_received()
        self.client.disconnect()

        self.assertEqual(len(received), 0)

    # @mock.patch('flask_login.utils._get_user')
    # def test_handle_data_with_login(self, _get_user):
    #     print()
    #
    #     user = UserMixin()
    #
    #     # current_user.return_value = user
    #     _get_user.return_value = user
    #
    #     print('test func', flask_login.utils._get_user())
    #
    #     self.client.emit(DATA_TOPIC, {'data': random.randint(10, 100)})
    #
    #     received = self.client.get_received()
    #
    #     self.client.disconnect()
    #
    #     self.assertEqual(len(received), 2)
    #     self.assertEqual(received[0]['name'], DATA_RESPONSE_TOPIC)
    #     self.assertEqual(received[1]['name'], COMMAND_TOPIC)


if __name__ == '__main__':
    unittest.main()
