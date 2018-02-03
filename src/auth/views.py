import requests
import validators
from flask import request, make_response, jsonify
from flask.views import MethodView

from .models import User


class DataAPI(MethodView):
    """
    Data Manipulation API
    """

    def post(self):
        # send data request
        post_data = request.get_json(force=True)
        auth_token = post_data.get('token', None)
        if auth_token:
            resp = User.decode_auth_token(auth_token)
            if not isinstance(resp, str):
                endpoint = post_data.get('endpoint', None)
                data = post_data.get('data', None)
                if not endpoint or not validators.url(endpoint):
                    response_object = {
                        'status': 'fail',
                        'message': 'Endpoint is not valid url.'
                    }
                    return make_response(jsonify(response_object)), 401
                if not data:
                    response_object = {
                        'status': 'fail',
                        'message': 'data required'
                    }
                    return make_response(jsonify(response_object)), 401
                user = User.query.filter_by(id=resp).first()
                if user is None:
                    response_object = {
                        'status': 'fail',
                        'message': 'User is not valid'
                    }
                    return make_response(jsonify(response_object)), 401
                request_object = {
                    'user_id': user.id,
                    'name': user.name,
                    'data': data
                }
                response = requests.post(endpoint, data=request_object)
                return make_response(response.text), 200
            response_object = {
                'status': 'fail',
                'message': resp
            }
            return make_response(jsonify(response_object)), 401
        else:
            response_object = {
                'status': 'fail',
                'message': 'Provide a valid auth token.'
            }
            return make_response(jsonify(response_object)), 401
