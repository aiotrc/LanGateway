import unittest

import _thread
from flask_login import login_user, LoginManager

from core import db, app
from core.control import LOGIN_PATH, DATA_PATH
from core.models import User
from core.mqtt_handler import MQTT_CLIENT_ID, MQTT_BROKER_HOST
from core.views import BAD_FORMAT_MESSAGE, BAD_TOKEN_MESSAGE, INVALID_TOKEN_MESSAGE, TOKEN_EXPIRED_MESSAGE, \
    LOGIN_MESSAGE, FIELD_IS_MISSING, DATA_SENT_MESSAGE
from test.mqtt_client_test import check_connection_established, check_connection_ack
from test.paho_mqtt_test_helper.broker import FakeBroker


class TestFlaskAPIs(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = cls.create_app()
        cls.app.login_manager.init_app(app)
        cls.client = cls.app.test_client()
        cls.client.testing = True

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

    def test_login_bad_request_format(self):
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

    def test_send_data_bad_request_format(self):
        rv = self.client.post(DATA_PATH)
        assert str.encode(BAD_FORMAT_MESSAGE) in rv.data

    def test_send_data_without_required_field(self):
        rv = self.client.post(DATA_PATH, data='{"key":"value"}')
        assert str.encode(FIELD_IS_MISSING('')) in rv.data

    def test_send_data_with_valid_fields(self):
        def send_request():
            rv = self.client.post(DATA_PATH, data='{"data":"thing data"}')
            assert str.encode(DATA_SENT_MESSAGE) in rv.data

        _thread.start_new_thread(send_request, ())

        fake_mqtt_broker = FakeBroker(port=1883)
        fake_mqtt_broker.start()
        check_connection_established(fake_mqtt_broker, MQTT_CLIENT_ID)

        check_connection_ack(fake_mqtt_broker)

        fake_mqtt_broker.receive_packet(1000)


if __name__ == '__main__':
    unittest.main()
