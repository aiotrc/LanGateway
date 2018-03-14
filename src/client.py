import logging
import random
import threading
import os
from multiprocessing import Process

from requests import post
from socketIO_client import BaseNamespace, SocketIO

from src import ROOT_DIR

COMMAND_TOPIC = 'command'
COMMAND_RESPONSE_TOPIC = 'command_response'

DATA_TOPIC = 'data'
DATA_RESPONSE_TOPIC = 'data_response'

HTTPS_HOST = 'localhost'
HTTPS_PORT = 5000
HTTPS_DATA_URI = 'https://{}:{}/data'.format(HTTPS_HOST, HTTPS_PORT)

SOCKETIO_HOST = 'localhost'
SOCKETIO_PORT = 5001

data_rate = 10


def send_data_https():
    pem_file_path = os.path.join(ROOT_DIR, 'server.pem')
    result = post(HTTPS_DATA_URI, json=dict(
        token='eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE1MjAyNTAwMDIsImlhdCI6MTUxNzY1ODAwMiwic3ViIjoxfQ'
              '.L5SZVHC1Pc2jdV88SP2a0Son6jDbUnSCbtaq8I_P9fQ',
        data='{"temp":"20"}'
    ), verify=pem_file_path)
    return result


class SocketioNamespace(BaseNamespace):
    def on_connect(self):
        print('[Connected]')

    def on_reconnect(self):
        print('[Reconnected]')

    def on_disconnect(self):
        print('[Disconnected]')



    @staticmethod
    def on_command(*args):
        print('on_command', args)
        socketio = SocketIO(SOCKETIO_HOST, SOCKETIO_PORT)
        if args[0].get('command') == 'set_data_rate':
            global data_rate
            data_rate = args[0].get('args')[0]
            print('set_data_rate:', data_rate)
        else:
            socketio.emit(COMMAND_RESPONSE_TOPIC, {'data': 'Command is not implemented!'})
            return
        socketio.emit(COMMAND_RESPONSE_TOPIC, {'data': 'Command is done'})

    @staticmethod
    def on_data_response(*args):
        print('on_data_response', args)


def socketio_start_listening():
    socketio = SocketIO(SOCKETIO_HOST, SOCKETIO_PORT, SocketioNamespace)
    socketio.on(COMMAND_TOPIC, SocketioNamespace.on_command)
    socketio.wait(seconds=60)
    socketio_start_listening()


def send_data():
    socketio = SocketIO(SOCKETIO_HOST, SOCKETIO_PORT, SocketioNamespace)
    socketio.on(DATA_RESPONSE_TOPIC, SocketioNamespace.on_data_response)
    socketio.emit(DATA_TOPIC, {'data': random.randint(10, 100)})
    socketio.wait(seconds=2)
    threading.Timer(data_rate, send_data, []).start()


def stop_all(processes=None):
    if processes is None:
        processes = []

    for process in processes:
        process.terminate()


if __name__ == '__main__':
    result = send_data_https()
    print(result)
    logging.getLogger('socketIO-client').setLevel(logging.DEBUG)
    logging.basicConfig()
    p_listen = Process(target=socketio_start_listening, args=())
    p_listen.start()
    p_send = Process(target=send_data, args=())
    p_send.start()
    # stop_all([p_listen, p_send])
