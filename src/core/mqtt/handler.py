"""
MQTT Handler
"""
from json.decoder import JSONDecodeError
from paho.mqtt.client import Client, MQTTv311
import json

from core.mqtt.config import publish_name, client_name, broker_address, broker_port, message_topic
from core.socketio_runner import send_message


def json_validation(my_json: json):
    print("json_validation")
    try:
        if my_json['id'] is None or my_json['byte_stream'] is None:
            return False
    except KeyError:
        return False
    return True


def is_valid(s: str):
    try:
        j = json.loads(s)
        if json_validation(j):
            return j
    except JSONDecodeError:
        return False


def push(s: str):
    j = is_valid(s)
    if not j:
        return False
    return True


def on_message_callback(client, userdata, message):
    print('on_message_callback: topic[' + message.topic + ']')
    if is_valid(message.payload):
        send_message(message.payload)
    else:
        print('Message payload not valid')


def on_publish_callback(client, userdata, mid):
    print('on_publish_callback')


def connect_callback(client, userdata, flags, rc):
    print('connect_callback: result code[' + str(rc) + ']')
    client.subscribe(publish_name)


def disconnect_callback(client, userdata, self):
    print('disconnect_callback')


def publish_message(message):
    print("publish_message")
    publish_client = Client(client_id=client_name, protocol=MQTTv311)
    publish_client.publish(topic=message_topic, payload=message)


if __name__ == '__main__':
    client = Client(client_id=client_name, protocol=MQTTv311)
    client.on_message = on_message_callback
    client.on_publish = on_publish_callback
    client.on_connect = connect_callback
    client.on_disconnect = disconnect_callback
    client.connect(host=broker_address, port=broker_port)
    client.loop_forever()

