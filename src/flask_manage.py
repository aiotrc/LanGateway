import datetime

import jwt
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from gevent.wsgi import WSGIServer

from core import app, db
from core.models import User

HTTPS_HOST = 'localhost'
HTTPS_PORT = 5000

# payload = {
#     'exp': datetime.datetime.utcnow(),
#     'iat': datetime.datetime.utcnow() - datetime.timedelta(days=30),
#     'sub': 1
# }
# token = jwt.encode(
#     payload,
#     app.config.get('SECRET_KEY'),
#     algorithm='HS256'
# )
# print(token)

manager = Manager(app)
migrate = Migrate(app, db)
# migrations
manager.add_command('db', MigrateCommand)


@manager.command
def create_db():
    """Creates the db tables."""
    db.create_all()


def init_db():

    thing1 = User(name='thing1')
    thing2 = User(name='thing2')

    db.session.add(thing1)
    db.session.add(thing2)
    db.session.commit()


@manager.command
def drop_db():
    """Drops the db tables."""
    db.drop_all()


def start_http_server():
    http_server = make_http_server()
    http_server.serve_forever()


def make_http_server():
    http_server = WSGIServer((HTTPS_HOST, HTTPS_PORT), app, keyfile='server.key', certfile='server.crt')
    return http_server


if __name__ == '__main__':
    create_db()
    init_db()
    start_http_server()
