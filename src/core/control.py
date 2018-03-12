from flask import Blueprint

from .views import DataAPI, ControlAPI, LoginAPI, LogoutAPI

LOGIN_PATH = '/login'
LOGOUT_PATH = '/logout'
DATA_PATH = '/data'
CONTROL_PATH = '/control'

blueprint = Blueprint('global_blueprint', __name__)

# define the API resources
login_view = LoginAPI.as_view('login_api')
logout_view = LogoutAPI.as_view('logout_api')
data_view = DataAPI.as_view('data_api')
control_view = ControlAPI.as_view('control_api')

# add Rules for API Endpoints
blueprint.add_url_rule(
    rule=LOGIN_PATH,
    view_func=login_view,
    methods=['POST']
)
blueprint.add_url_rule(
    rule=LOGOUT_PATH,
    view_func=logout_view,
    methods=['POST']
)
blueprint.add_url_rule(
    rule=DATA_PATH,
    view_func=data_view,
    methods=['POST']
)
blueprint.add_url_rule(
    rule=CONTROL_PATH,
    view_func=control_view,
    methods=['POST']
)
