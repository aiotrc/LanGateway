"""
MQTT Handler
"""
import json

from flask_socketio import SocketIO
from paho.mqtt.client import Client, MQTTv311
from paho.mqtt.publish import single


class MqttHandler:
    def __init__(self, client_id='DEFAULT_CLIENT_ID', topic='DEFAULT_TOPIC', broker_host='localhost', broker_port=1883):
        self.client_id = client_id
        self.client = Client(client_id=self.client_id, protocol=MQTTv311)
        self.client.on_message = self.on_message_callback
        self.client.on_publish = self.on_publish_callback
        self.client.on_connect = self.connect_callback
        self.client.on_disconnect = self.disconnect_callback
        self.topic = topic
        self.broker_host = broker_host
        self.broker_port = broker_port

    def connect(self):
        self.client.connect(host=self.broker_host, port=self.broker_port)

    def connect_callback(self, client, userdata, flags, rc):
        print('connect_callback: result code[' + str(rc) + ']')
        client.subscribe(topic=self.topic)

    def disconnect_callback(self, client, userdata, rc):
        print('disconnect_callback')

    def is_valid(self, my_json: json):
        print("json_validation")
        # try:
        #     if my_json['id'] is None or my_json['byte_stream'] is None:
        #         return False
        # except KeyError:
        #     return False
        return True

    def on_message_callback(self, client, userdata, message):
        print('on_message_callback: topic[' + message.topic + ']')
        if self.is_valid(message.payload):
            socketio = SocketIO()
            socketio.emit(message.topic, {'data': message.payload})
        else:
            print('Message payload not valid')

    @staticmethod
    def publish_single_message(topic, payload=None, qos=0, retain=False, hostname="localhost",
                               port=1883, client_id="", keepalive=60, will=None, auth=None, tls=None):
        print("publish_single_message")
        single(topic=topic, payload=payload, qos=qos, retain=retain, hostname=hostname, port=port, client_id=client_id,
               keepalive=keepalive, will=will, auth=auth, tls=tls)

    def on_publish_callback(self, client, userdata, mid):
        print('on_publish_callback')

    def loop_for_ever(self):
        self.client.loop_forever()


if __name__ == '__main__':
    # 172.23.132.37 / iot.eclipse.org
    mqtt_handler = MqttHandler(client_id='LAN_GATEWAY', topic='LAN_GATEWAY_TOPIC', broker_host='172.23.132.37')
    mqtt_handler.connect()
    mqtt_handler.loop_for_ever()
