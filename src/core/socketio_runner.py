from flask_socketio import SocketIO, send

from core import app

socketio = SocketIO(app)


@socketio.on('data_json')
def handle_message(data_json):
    print('received json: ' + str(data_json))
    send('got:' + str(data_json))


def send_message(data_json):
    send(data_json, json=True)


if __name__ == '__main__':
    socketio.run(app=app, host='localhost', port=5001)
