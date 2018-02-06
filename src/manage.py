from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from gevent.wsgi import WSGIServer

from core import app, db

# payload = {
#     'exp': datetime.datetime.utcnow() + datetime.timedelta(days=30),
#     'iat': datetime.datetime.utcnow(),
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


@manager.command
def drop_db():
    """Drops the db tables."""
    db.drop_all()


if __name__ == '__main__':
    http_server = WSGIServer(('localhost', 5000), app, keyfile='server.key', certfile='server.crt')
    http_server.serve_forever()

