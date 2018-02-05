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


def on_message(client, userdata, message):
    print('on_message: topic[' + message.topic + ']')
    if is_valid(message.payload):
        send_message(message.payload)
    else:
        print('Message payload not valid')


def on_publish(client, userdata, result):
    print('on_publish')


def on_connect(client, userdata, flags, rc):
    print('on_connect: result code[' + str(rc) + ']')
    client.subscribe(publish_name)


def on_disconnect(client, userdata, rc):
    print('on_disconnect')


def publish_message(message):
    client.publish(topic=message_topic, payload=message)


client = Client(client_id=client_name, protocol=MQTTv311)
client.on_message = on_message
client.on_publish = on_publish
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.connect(host=broker_address, port=broker_port)
client.loop_forever()

