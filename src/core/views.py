import requests
import validators
from flask import request, make_response, jsonify
from flask.views import MethodView

from core.mqtt.handler import publish_message
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
                publish_message(data)
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

