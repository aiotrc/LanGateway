import datetime

import jwt
from flask_login import UserMixin

from core import db, app
from core import login_manager

JWT_ALGORITHM = 'HS256'


class User(db.Model, UserMixin):
    """ User Model for storing user related details """
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=True)

    def __init__(self, name="Unknown"):
        self.name = name

    def encode_auth_token(self, user_id):
        """
        Generates the Auth Token
        :return: string
        """
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=30),
                'iat': datetime.datetime.utcnow(),
                'sub': user_id
            }
            return jwt.encode(
                payload,
                app.config.get('SECRET_KEY'),
                algorithm=JWT_ALGORITHM)
        except Exception as e:
            return e

    @staticmethod
    def decode_auth_token(auth_token):
        from core.views import BLACK_LIST_TOKEN_MESSAGE, TOKEN_EXPIRED_MESSAGE, INVALID_TOKEN_MESSAGE
        """
        Validates the core token
        :param auth_token:
        :return: integer|string
        """
        try:
            payload = jwt.decode(auth_token, app.config.get('SECRET_KEY'), algorithms=JWT_ALGORITHM,
                                 verify_exp=True)
            is_blacklisted_token = BlacklistToken.check_blacklist(auth_token)
            if is_blacklisted_token:
                return BLACK_LIST_TOKEN_MESSAGE
            else:
                return payload['sub']
        except jwt.ExpiredSignatureError:
            return TOKEN_EXPIRED_MESSAGE
        except jwt.InvalidTokenError:
            return INVALID_TOKEN_MESSAGE


@login_manager.user_loader
def get_user(ident):
    return User.query.get(int(ident))


class BlacklistToken(db.Model):
    """
    Token Model for storing JWT tokens
    """
    __tablename__ = 'blacklist_tokens'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    token = db.Column(db.String(1000), unique=True, nullable=False)
    blacklisted_on = db.Column(db.DateTime, nullable=False)

    def __init__(self, token):
        self.token = token
        self.blacklisted_on = datetime.datetime.now()

    def __repr__(self):
        return '<id: token: {}'.format(self.token)

    @staticmethod
    def check_blacklist(auth_token):
        # check whether core token has been blacklisted
        res = BlacklistToken.query.filter_by(token=str(auth_token)).first()
        if res:
            return True
        else:
            return False
