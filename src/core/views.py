import datetime

from flask import request, make_response, jsonify
from flask.views import MethodView
from flask_login import login_user, login_required

from core import db, app
from core.mqtt_handler import MqttHandler, MQTT_BROKER_HOST, MQTT_CLIENT_ID, MQTT_TOPIC
from .models import User

SUCCESS = 'success'
FAIL = 'fail'
BAD_FORMAT_MESSAGE = 'Request data format should be JSON'
BAD_TOKEN_MESSAGE = 'Provide a valid core token'
BLACK_LIST_TOKEN_MESSAGE = 'Token blacklisted'
TOKEN_EXPIRED_MESSAGE = 'Signature expired'
INVALID_TOKEN_MESSAGE = 'Invalid token'
LOGIN_MESSAGE = 'Logged in'
FIELD_IS_MISSING = lambda field_name: '{} field is missing'.format(field_name)


class LoginAPI(MethodView):

    def post(self):
        try:
            post_data = request.get_json(force=True)
        except:
            return generate_response(FAIL, BAD_FORMAT_MESSAGE)

        auth_token = post_data.get('token', None)

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
            return generate_response(FAIL, BAD_TOKEN_MESSAGE)


class DataAPI(MethodView):
    """
    Data Manipulation API
    """

    @login_required
    def post(self):
        # send data request
        try:
            post_data = request.get_json(force=True)
        except:
            return generate_response(FAIL, BAD_FORMAT_MESSAGE)

        data = post_data.get('data', None)

        if not data:
            return generate_response('fail', FIELD_IS_MISSING('data'))

        # send data to platform
        mqtt_handler = MqttHandler(client_id=MQTT_CLIENT_ID, topic=MQTT_TOPIC,
                                   broker_host=MQTT_BROKER_HOST)
        mqtt_handler.publish_single_message(topic=mqtt_handler.topic, payload=data,
                                            hostname=mqtt_handler.broker_host,
                                            client_id=mqtt_handler.client_id)
        return generate_response(SUCCESS, LOGIN_MESSAGE)


class ControlAPI(MethodView):
    """
    Control API
    """

    def post(self):
        post_data = request.get_json(force=True)
        command_type = post_data.get('type', None)
        command_data = post_data.get('data', None)
        if not command_type:
            response_object = {
                'status': 'fail',
                'message': 'Provide type attribute.'
            }
            return make_response(jsonify(response_object)), 401
        if not command_data:
            response_object = {
                'status': 'fail',
                'message': 'Provide data attribute.'
            }
            return make_response(jsonify(response_object)), 401

        if command_type == 'new_thing':
            name = command_data.get('name', None)
            user = User(
                name=name
            )
            user.token = user.encode_auth_token(user.id)
            # insert the user
            db.session.add(user)
            db.session.commit()
            # generate the auth token
            auth_token = user.encode_auth_token(user.id)
            response_object = {
                'status': 'success',
                'message': 'Successfully registered.',
                'auth_token': auth_token.decode()
            }
            return make_response(jsonify(response_object)), 201
        else:
            response_object = {
                'status': 'fail',
                'message': 'Requested type not supported.'
            }
            return make_response(jsonify(response_object)), 401


def generate_response(status, message):
    response_object = {
        'status': status,
        'message': message
    }
    code = 200
    if status == FAIL:
        code = 401
    return make_response(jsonify(response_object)), code
