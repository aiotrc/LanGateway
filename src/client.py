import json
import logging
import random
import threading
import os
from multiprocessing import Process

import requests
from socketIO_client import BaseNamespace, SocketIO

from core.control import LOGIN_PATH, DATA_PATH
from core.models import User
from core.socketio_runner import SOCKETIO_HOST, SOCKETIO_PORT, COMMAND_RESPONSE_TOPIC, COMMAND_TOPIC, \
    DATA_RESPONSE_TOPIC, DATA_TOPIC, SIO_COMMAND_FIELD, SIO_ARGS_FIELD, SIO_DATA_FIELD, COMMAND_SET_DATA_RATE
from core.views import DATA_FIELD
from flask_manage import HTTPS_HOST, HTTPS_PORT
from src import ROOT_DIR
from test.paho_mqtt_test_helper.broker import FakeBroker

HTTPS_URI = lambda url: 'https://{}:{}{}'.format(HTTPS_HOST, HTTPS_PORT, url)
data_rate = 10


def https_login(session):
    pem_file_path = os.path.join(ROOT_DIR, 'server.pem')
    valid_token = User.encode_auth_token(1).decode('utf-8')
    result = session.post(HTTPS_URI(LOGIN_PATH), json=dict(
        token=valid_token
    ), verify=pem_file_path)
    print(result.text)


def https_send_data(session):
    pem_file_path = os.path.join(ROOT_DIR, 'server.pem')
    result = session.post(HTTPS_URI(DATA_PATH), json=dict(
        data=json.dumps({DATA_FIELD: 'thing data'})
    ), verify=pem_file_path)
    print(result.text)


class SocketioNamespace(BaseNamespace):
    def on_connect(self):
        print('[Connected]')

    def on_reconnect(self):
        print('[Reconnected]')

    def on_disconnect(self):
        print('[Disconnected]')

    def on_command(self, *args):
        print('on_command', args)
        if args[0].get(SIO_COMMAND_FIELD) == COMMAND_SET_DATA_RATE:
            global data_rate
            data_rate = args[0].get(SIO_ARGS_FIELD)[0]
            print(COMMAND_SET_DATA_RATE, data_rate)
        else:
            self.emit(COMMAND_RESPONSE_TOPIC, {SIO_DATA_FIELD: 'Command is not implemented!'})
            return
        self.emit(COMMAND_RESPONSE_TOPIC, {SIO_DATA_FIELD: 'Command is done'})

    @staticmethod
    def on_data_response(*args):
        print('on_data_response', args)


def socketio_start_listening(cookies):
    socketio = SocketIO(SOCKETIO_HOST, SOCKETIO_PORT, SocketioNamespace, cookies=cookies)
    socketio.wait(seconds=60)
    socketio_start_listening(cookies)


def send_data(cookies):
    socketio = SocketIO(SOCKETIO_HOST, SOCKETIO_PORT, SocketioNamespace, cookies=cookies)
    socketio.on(DATA_RESPONSE_TOPIC, SocketioNamespace.on_data_response)
    socketio.emit(DATA_TOPIC, {'data': random.randint(10, 100)})
    socketio.wait(seconds=5)
    threading.Timer(data_rate, send_data, [cookies]).start()


def stop_all(processes=list()):
    for process in processes:
        process.terminate()


if __name__ == '__main__':
    session = requests.Session()
    https_login(session)
    https_send_data(session)

    cookies = session.cookies.get_dict()

    logging.getLogger('socketIO-client').setLevel(logging.DEBUG)
    logging.basicConfig()

    p_listen = Process(target=socketio_start_listening, args=(cookies,))
    p_listen.start()

    p_send = Process(target=send_data, args=(cookies,))
    p_send.start()
    # stop_all([p_listen, p_send])
