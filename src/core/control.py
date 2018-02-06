from flask import Blueprint

from .views import DataAPI, ControlAPI

blueprint = Blueprint('global_blueprint', __name__)

# define the API resources
data_view = DataAPI.as_view('data_api')
control_view = ControlAPI.as_view('control_api')

# add Rules for API Endpoints
blueprint.add_url_rule(
    rule='/data',
    view_func=data_view,
    methods=['POST']
)
blueprint.add_url_rule(
    rule='/control',
    view_func=control_view,
    methods=['POST']
)
