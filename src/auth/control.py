from flask import Blueprint

from src.auth.views import DataAPI

data = Blueprint('data', __name__)
# define the API resources
data_view = DataAPI.as_view('data_api')

# add Rules for API Endpoints
data.add_url_rule(
    '/data',
    view_func=data_view,
    methods=['POST']
)
