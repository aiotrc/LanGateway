import random
import unittest

from core import app
from core.socketio_runner import socketio, DATA_RESPONSE_TOPIC, DATA_TOPIC, COMMAND_TOPIC


class TestClient(unittest.TestCase):

    def test_handle_data(self):
        client = socketio.test_client(app)
        client.emit(DATA_TOPIC, {'data': random.randint(10, 100)})

        received = client.get_received()
        client.disconnect()

        self.assertEqual(len(received), 2)
        self.assertEqual(received[0]['name'], DATA_RESPONSE_TOPIC)
        self.assertEqual(received[1]['name'], COMMAND_TOPIC)


if __name__ == '__main__':
    unittest.main()
