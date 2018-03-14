import _thread
import json
import unittest
from unittest import mock

from core import db, app
from core.control import LOGIN_PATH, DATA_PATH, LOGOUT_PATH, CONTROL_PATH
from core.models import User
from core.mqtt_handler import MQTT_CLIENT_ID
from core.views import BAD_FORMAT_MESSAGE, INVALID_TOKEN_MESSAGE, TOKEN_EXPIRED_MESSAGE, \
    LOGIN_MESSAGE, FIELD_IS_MISSING, DATA_SENT_MESSAGE, LOGOUT_MESSAGE, TOKEN_FIELD, DATA_FIELD, COMMAND_TYPE_FIELD, \
    COMMAND_ARGS_FIELD, BAD_COMMAND_MESSAGE, COMMAND_TYPE_NEW_THING, NAME_FIELD, SUCCESS, MESSAGE, \
    NOT_AUTHORIZED_MESSAGE
from test.mqtt_client_test import check_connection_established, check_connection_ack
from test.paho_mqtt_test_helper.broker import FakeBroker


class TestFlaskAPIsBase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = cls.create_app()
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

        thing2 = User(name='thing2')
        self.valid_token = User.encode_auth_token(1).decode('utf-8')

        db.session.add(thing1)
        db.session.add(thing2)
        db.session.commit()

    def login(self, token=None):
        if not token:
            token = self.valid_token
        self.login_user(self.client, token)

    @staticmethod
    def login_user(client, token):
        rv = client.post(LOGIN_PATH, data=json.dumps({TOKEN_FIELD: token}))
        assert str.encode(LOGIN_MESSAGE) in rv.data

    def logout(self):
        self.logout_user(self.client)

    @staticmethod
    def logout_user(client):
        rv = client.post(LOGOUT_PATH)
        assert str.encode(LOGOUT_MESSAGE) in rv.data


class TestLoginLogout(TestFlaskAPIsBase):
    def test_login_bad_request_format(self):
        rv = self.client.post(LOGIN_PATH)
        assert str.encode(BAD_FORMAT_MESSAGE) in rv.data

    def test_login_without_token(self):
        rv = self.client.post(LOGIN_PATH, data=json.dumps({'key': 'value'}))
        assert str.encode(FIELD_IS_MISSING(TOKEN_FIELD)) in rv.data

    def test_login_with_invalid_token(self):
        rv = self.client.post(LOGIN_PATH, data=json.dumps({TOKEN_FIELD: 'invalid'}))
        assert str.encode(INVALID_TOKEN_MESSAGE) in rv.data

    def test_login_with_expired_token(self):
        rv = self.client.post(LOGIN_PATH, data=json.dumps({TOKEN_FIELD: self.expired_token}))
        assert str.encode(TOKEN_EXPIRED_MESSAGE) in rv.data

    def test_login_logout(self):
        self.login()
        self.logout()


class TestDataAPI(TestFlaskAPIsBase):
    def setUp(self):
        super(TestDataAPI, self).setUp()
        self.login()

    def tearDown(self):
        self.logout()
        super(TestDataAPI, self).tearDown()

    def test_send_data_without_login(self):
        self.logout()
        rv = self.client.post(DATA_PATH)
        assert str.encode('401 Unauthorized') in rv.data
        self.login()

    def test_send_data_bad_request_format(self):
        rv = self.client.post(DATA_PATH)
        assert str.encode(BAD_FORMAT_MESSAGE) in rv.data

    def test_send_data_without_required_field(self):
        rv = self.client.post(DATA_PATH, data=json.dumps({'key': 'value'}))
        assert str.encode(FIELD_IS_MISSING(DATA_FIELD)) in rv.data

    def test_send_data_with_valid_fields(self):
        def send_request():
            rv = self.client.post(DATA_PATH, data=json.dumps({DATA_FIELD: 'thing data'}))
            assert str.encode(DATA_SENT_MESSAGE) in rv.data

        _thread.start_new_thread(send_request, ())

        fake_mqtt_broker = FakeBroker(port=1883)
        fake_mqtt_broker.start()

        check_connection_established(fake_mqtt_broker, MQTT_CLIENT_ID)
        check_connection_ack(fake_mqtt_broker)
        fake_mqtt_broker.receive_packet(1000)


class TestControlAPI(TestFlaskAPIsBase):
    def test_send_command_not_local(self):
        rv = self.client.post(CONTROL_PATH, headers={'host': 'example.com'})
        assert str.encode(NOT_AUTHORIZED_MESSAGE) in rv.data

    def test_send_command_bad_request_format(self):
        rv = self.client.post(CONTROL_PATH)
        assert str.encode(BAD_FORMAT_MESSAGE) in rv.data

    def test_send_command_without_required_fields(self):
        r1 = self.client.post(CONTROL_PATH, data=json.dumps({'key': 'value'}))
        r2 = self.client.post(CONTROL_PATH, data=json.dumps({COMMAND_TYPE_FIELD: 'command type'}))
        assert str.encode(FIELD_IS_MISSING(COMMAND_TYPE_FIELD)) in r1.data
        assert str.encode(FIELD_IS_MISSING(COMMAND_ARGS_FIELD)) in r2.data

    def test_send_unknown_command(self):
        rv = self.client.post(CONTROL_PATH,
                              data=json.dumps({COMMAND_TYPE_FIELD: 'unknown command', COMMAND_ARGS_FIELD: 'arg'}))
        assert str.encode(BAD_COMMAND_MESSAGE) in rv.data

    def test_send_valid_command(self):
        new_thing_name = 'another new thing'

        users = User.query.all()
        num_users_before = len(users)

        rv = self.client.post(CONTROL_PATH,
                              data=json.dumps({COMMAND_TYPE_FIELD: COMMAND_TYPE_NEW_THING,
                                               COMMAND_ARGS_FIELD: {NAME_FIELD: new_thing_name}}))
        assert str.encode(SUCCESS) in rv.data

        users = User.query.all()
        num_users_after = len(users)
        assert num_users_after == num_users_before + 1

        response = json.loads(rv.data)
        message = json.loads(response.get(MESSAGE, None))
        assert message

        new_token = message.get(TOKEN_FIELD, None)
        assert new_token

        self.login(token=new_token)
        self.logout()


if __name__ == '__main__':
    unittest.main()
