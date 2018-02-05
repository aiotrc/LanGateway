from flask import Blueprint

from .views import DataAPI

data_blueprint = Blueprint('data', __name__)
# define the API resources
data_view = DataAPI.as_view('data_api')

# add Rules for API Endpoints
data_blueprint.add_url_rule(
    '/data',
    view_func=data_view,
    methods=['POST']
)
