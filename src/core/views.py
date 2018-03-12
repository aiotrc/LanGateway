import datetime
import json

from flask import request, make_response, jsonify
from flask_login import logout_user
from flask.views import MethodView
from flask_login import login_user, login_required

from core import db, app
from core.mqtt_handler import MqttHandler, MQTT_BROKER_HOST, MQTT_CLIENT_ID, MQTT_TOPIC
from .models import User

MESSAGE = 'message'
STATUS = 'status'
SUCCESS = 'success'
FAIL = 'fail'

BAD_FORMAT_MESSAGE = 'Request data format should be JSON'
FIELD_IS_MISSING = lambda field_name: '{} field is missing'.format(field_name)

TOKEN_FIELD = 'token'
BLACK_LIST_TOKEN_MESSAGE = 'Token blacklisted'
TOKEN_EXPIRED_MESSAGE = 'Signature expired'
INVALID_TOKEN_MESSAGE = 'Invalid token'
LOGIN_MESSAGE = 'Logged in'

LOGOUT_MESSAGE = 'Logged out'

DATA_FIELD = 'data'
DATA_SENT_MESSAGE = 'Data Sent'

COMMAND_TYPE_FIELD = 'type'
COMMAND_ARGS_FIELD = 'args'
COMMAND_TYPE_NEW_THING = 'new_thing'
COMMAND_SUCCESSFUL_MESSAGE = lambda command_type: 'Command {} run successfully'.format(command_type)
BAD_COMMAND_MESSAGE = 'Command type not supported'
NAME_FIELD = 'name'


class LoginAPI(MethodView):
    def post(self):
        """
        Request: data:{"token":"<user token>"}
        :return: error or logs the user in
        """
        try:
            post_data = request.get_json(force=True)
        except:
            return generate_response(FAIL, BAD_FORMAT_MESSAGE)

        auth_token = post_data.get(TOKEN_FIELD, None)

        if auth_token:
            resp = User.decode_auth_token(auth_token)
            # check whether a user id is returned
            if not isinstance(resp, str):
                user = User.query.filter_by(id=resp).first()
                login_user(user=user, remember=True,
                           duration=datetime.timedelta(days=app.config.get('LOGIN_REMEMBER_DAYS', 10)))
                return generate_response(SUCCESS, LOGIN_MESSAGE)
            else:
                return generate_response(FAIL, resp)
        else:
            return generate_response(FAIL, FIELD_IS_MISSING(TOKEN_FIELD))


class LogoutAPI(MethodView):
    def post(self):
        logout_user()

        return generate_response(SUCCESS, LOGOUT_MESSAGE)


class DataAPI(MethodView):
    @login_required
    def post(self):
        """
        send data to platform using MQTT
        Request: data:{"data":"thing data"}
        :return: error or successful send message
        """
        try:
            post_data = request.get_json(force=True)
        except:
            return generate_response(FAIL, BAD_FORMAT_MESSAGE)

        data = post_data.get(DATA_FIELD, None)

        if not data:
            return generate_response(FAIL, FIELD_IS_MISSING(DATA_FIELD))

        # send data to platform
        MqttHandler.publish_single_message(topic=MQTT_TOPIC, payload=data,
                                           hostname=MQTT_BROKER_HOST,
                                           client_id=MQTT_CLIENT_ID)
        return generate_response(SUCCESS, DATA_SENT_MESSAGE)


class ControlAPI(MethodView):
    def post(self):
        """
        receives command and executes it
        Request: data:{"type":"new_thing", "args":{"name":"<thing name>"}}
        :return: error or command successful message with results
        """
        print(request.host)
        try:
            post_data = request.get_json(force=True)
        except:
            return generate_response(FAIL, BAD_FORMAT_MESSAGE)

        command_type = post_data.get(COMMAND_TYPE_FIELD, None)
        command_args = post_data.get(COMMAND_ARGS_FIELD, None)

        if not command_type:
            return generate_response(FAIL, FIELD_IS_MISSING(COMMAND_TYPE_FIELD))
        if not command_args:
            return generate_response(FAIL, FIELD_IS_MISSING(COMMAND_ARGS_FIELD))

        if command_type == COMMAND_TYPE_NEW_THING:
            name = command_args.get(NAME_FIELD, None)
            user = User(name=name)

            db.session.add(user)
            db.session.commit()

            auth_token = user.encode_auth_token(user.id).decode('utf-8')

            return generate_response(SUCCESS, json.dumps({TOKEN_FIELD: auth_token}))
        else:
            return generate_response(FAIL, BAD_COMMAND_MESSAGE)


def generate_response(status, message):
    response_object = {
        STATUS: status,
        MESSAGE: message
    }
    code = 200
    if status == FAIL:
        code = 401
    return make_response(jsonify(response_object)), code
