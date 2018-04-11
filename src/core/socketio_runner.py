import random

from flask_login import current_user
from flask_socketio import SocketIO, emit, join_room
from flask_socketio import disconnect

from core import app, socketio
from core.mqtt_handler import MqttHandler, MQTT_TOPIC, MQTT_BROKER_HOST, MQTT_CLIENT_ID

COMMAND_TOPIC = 'command'
COMMAND_RESPONSE_TOPIC = 'command_response'
DATA_TOPIC = 'data'
DATA_RESPONSE_TOPIC = 'data_response'

SIO_DATA_FIELD = 'data'
SIO_COMMAND_FIELD = 'command'
SIO_ARGS_FIELD = 'args'
SIO_ROOM_FIELD = 'room'

SOCKETIO_HOST = 'localhost'
SOCKETIO_PORT = 5001

ROOM_NAME = lambda thing_id: 'THING_{}'.format(thing_id)

COMMAND_SET_DATA_RATE = 'set_data_rate'

@socketio.on('connect')
def connect_handler():
    if current_user.is_authenticated:
        join_room(ROOM_NAME(current_user.id))
    else:
        disconnect()
        return False  # not allowed here


@socketio.on(DATA_TOPIC)
def handle_data(data_json):
    print('received json: ' + str(data_json))
    MqttHandler.publish_single_message(topic=MQTT_TOPIC, payload=str(data_json),
                                       hostname=MQTT_BROKER_HOST,
                                       client_id=MQTT_CLIENT_ID)

    emit(DATA_RESPONSE_TOPIC, {SIO_DATA_FIELD: 'Got it!'}, json=True)
    emit(COMMAND_TOPIC, {SIO_COMMAND_FIELD: COMMAND_SET_DATA_RATE, SIO_ARGS_FIELD: [random.randint(10, 20)]}, json=True)


@socketio.on(COMMAND_RESPONSE_TOPIC)
def handle_command_response(command_response_json):
    print('received json: ' + str(command_response_json))
    MqttHandler.publish_single_message(topic=MQTT_TOPIC, payload=str(command_response_json),
                                       hostname=MQTT_BROKER_HOST,
                                       client_id=MQTT_CLIENT_ID)


def emit_command(topic, payload):
    socketio = SocketIO(app)
    socketio.emit(topic, {SIO_COMMAND_FIELD: payload.get(SIO_COMMAND_FIELD),
                          SIO_ARGS_FIELD: payload.get(SIO_ARGS_FIELD)},
                  json=True, room=ROOM_NAME(payload.get(SIO_ROOM_FIELD)))


if __name__ == '__main__':
    socketio.run(app=app, host=SOCKETIO_HOST, port=SOCKETIO_PORT)
