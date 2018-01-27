import requests
import validators
from flask import request, make_response, jsonify
from flask.views import MethodView

from src.auth.models import User


class DataAPI(MethodView):
    """
    Data Manipulation API
    """

    def post(self):
        # send data request
        post_data = request.get_json()
        auth_token = post_data.get('token')
        if auth_token:
            resp = User.decode_auth_token(auth_token)
            if not isinstance(resp, str):
                endpoint = post_data.get('endpoint')
                data = post_data.get('data')
                if not validators.url(endpoint):
                    response_object = {
                        'status': 'fail',
                        'message': 'Endpoint is not valid url.'
                    }
                    return make_response(jsonify(response_object)), 401
                user = User.query.filter_by(id=resp).first()
                request_object = {
                    'user_id': user.id,
                    'name': user.name,
                    'data': data
                }
                response = requests.post(endpoint, data=request_object)
                return make_response(response.json()), 200
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
