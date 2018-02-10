from flask_socketio import SocketIO, send

from core import app
from core.mqtt.handler import MqttHandler

socketio = SocketIO(app)


@socketio.on('DATA_JSON')
def handle_message(data_json):
    print('received json: ' + str(data_json))
    mqtt_handler = MqttHandler(client_id='LAN_GATEWAY', topic='LAN_GATEWAY_TOPIC', broker_host='iot.eclipse.org')
    mqtt_handler.publish_single_message(topic=mqtt_handler.topic, payload=str(data_json), hostname=mqtt_handler.broker_host,
                                        client_id=mqtt_handler.client_id)


def send_message(data_json):
    send(data_json, json=True)


if __name__ == '__main__':
    socketio.run(app=app, host='localhost', port=5001)
