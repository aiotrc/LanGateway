from flask import request, make_response, jsonify
from flask.views import MethodView

from core import db
from core.mqtt_handler import MqttHandler
from .models import User


class DataAPI(MethodView):
    """
    Data Manipulation API
    """

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
                                           broker_host='iot.eclipse.org')
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