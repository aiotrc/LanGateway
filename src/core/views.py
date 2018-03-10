import datetime

from flask import request, make_response, jsonify
from flask.views import MethodView
from flask_login import login_user, login_required

from core import db, app
from core.mqtt_handler import MqttHandler, MQTT_BROKER_HOST
from .models import User

BAD_FORMAT_MESSAGE = 'Request data format should be JSON'
BAD_TOKEN_MESSAGE = 'Provide a valid core token'
BLACK_LIST_TOKEN_MESSAGE = 'Token blacklisted'
TOKEN_EXPIRED_MESSAGE = 'Signature expired'
INVALID_TOKEN_MESSAGE = 'Invalid token'
LOGIN_MESSAGE = 'Logged in'


class LoginAPI(MethodView):

    def post(self):
        try:
            post_data = request.get_json(force=True)
        except:
            return self.generate_response('fail', BAD_FORMAT_MESSAGE)

        auth_token = post_data.get('token', None)

        if auth_token:
            resp = User.decode_auth_token(auth_token)
            # check whether a user id is returned
            if not isinstance(resp, str):
                user = User.query.filter_by(id=resp).first()
                login_user(user=user, remember=True,
                           duration=datetime.timedelta(days=app.config.get('LOGIN_REMEMBER_DAYS', 10)))
                return self.generate_response('success', LOGIN_MESSAGE)
            else:
                return self.generate_response('fail', resp)
        else:
            return self.generate_response('fail', BAD_TOKEN_MESSAGE)

    @staticmethod
    def generate_response(status, message):
        response_object = {
            'status': status,
            'message': message
        }
        return make_response(jsonify(response_object)), 401


class DataAPI(MethodView):
    """
    Data Manipulation API
    """

    @login_required
    def post(self):
        # send data request
        post_data = request.get_json(force=True)
        auth_token = post_data.get('token', None)
        # check for token field
        if auth_token:
            resp = User.decode_auth_token(auth_token)
            # check whether a user id is returned
            if not isinstance(resp, str):

                data = post_data.get('data', None)
                # check for data field
                if not data:
                    response_object = {
                        'status': 'fail',
                        'message': 'data required'
                    }
                    return make_response(jsonify(response_object)), 401
                user = User.query.filter_by(id=resp).first()
                # check whether user with provided id exists in database
                if user is None:
                    response_object = {
                        'status': 'fail',
                        'message': 'User is not valid'
                    }
                    return make_response(jsonify(response_object)), 401
                # send data to platform
                mqtt_handler = MqttHandler(client_id='LAN_GATEWAY', topic='LAN_GATEWAY_TOPIC',
                                           broker_host=MQTT_BROKER_HOST)
                mqtt_handler.publish_single_message(topic=mqtt_handler.topic, payload=data,
                                                    hostname=mqtt_handler.broker_host,
                                                    client_id=mqtt_handler.client_id)
                response_object = {
                    'status': 'success',
                    'message': 'Data transferred'
                }
                # return result from endpoint
                return make_response(jsonify(response_object)), 200
            response_object = {
                'status': 'fail',
                'message': resp
            }
            return make_response(jsonify(response_object)), 401
        else:
            response_object = {
                'status': 'fail',
                'message': 'Provide a valid core token.'
            }
            return make_response(jsonify(response_object)), 401


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
