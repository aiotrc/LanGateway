import random

from flask_socketio import SocketIO, emit

from core import app, app_settings
from core.mqtt_handler import MqttHandler, MQTT_TOPIC, MQTT_BROKER_HOST, MQTT_CLIENT_ID

COMMAND_TOPIC = 'command'
COMMAND_RESPONSE_TOPIC = 'command_response'
DATA_TOPIC = 'data'
DATA_RESPONSE_TOPIC = 'data_response'

socketio = SocketIO(app)


@socketio.on(DATA_TOPIC)
def handle_data(data_json):
    print('received json: ' + str(data_json))
    MqttHandler.publish_single_message(topic=MQTT_TOPIC, payload=str(data_json),
                                       hostname=MQTT_BROKER_HOST,
                                       client_id=MQTT_CLIENT_ID)
    emit(DATA_RESPONSE_TOPIC, {'data': 'Got it!'}, json=True)
    emit(COMMAND_TOPIC, {'command': 'set_data_rate', 'args': [random.randint(10, 20)]}, json=True)


@socketio.on(COMMAND_RESPONSE_TOPIC)
def handle_command_response(command_response_json):
    print('received json: ' + str(command_response_json))
    MqttHandler.publish_single_message(topic=MQTT_TOPIC, payload=str(command_response_json),
                                       hostname=MQTT_BROKER_HOST,
                                       client_id=MQTT_CLIENT_ID)


def emit_command(topic, payload):
    if app_settings.DEBUG:
        print('on_message_callback: topic[' + topic + ']')
    socketio = SocketIO(app)
    socketio.emit(COMMAND_TOPIC, {'command': payload.get('command'),
                                  'args': payload.get('args')}, json=True)


if __name__ == '__main__':
    socketio.run(app=app, host='localhost', port=5001)
