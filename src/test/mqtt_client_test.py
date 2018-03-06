import unittest

from core.mqtt_handler import MqttHandler, MQTT_PROTOCOL_VERSION
from test.paho_mqtt_test_helper import paho_test
from test.paho_mqtt_test_helper.broker import FakeBroker

CLIENT_ID = 'test_connection_client'


class TestConnection(unittest.TestCase):

    def test_connect_success(self):
        mqttc = MqttHandler(client_id=CLIENT_ID, topic='test_topic', broker_host='localhost', broker_port=1888)
        mqttc.connect_async()
        mqttc.loop_start()

        fake_broker = FakeBroker()
        fake_broker.start()

        connect_packet = paho_test.gen_connect(
            CLIENT_ID, keepalive=60,
            proto_ver=MQTT_PROTOCOL_VERSION)
        packet_in = fake_broker.receive_packet(1000)
        assert packet_in  # Check connection was not closed
        assert packet_in == connect_packet

        connack_packet = paho_test.gen_connack(rc=0)
        count = fake_broker.send_packet(connack_packet)
        assert count  # Check connection was not closed
        assert count == len(connack_packet)

        mqttc.disconnect()
        disconnect_packet = paho_test.gen_disconnect()
        packet_in = fake_broker.receive_packet(1000)
        assert packet_in  # Check connection was not closed
        assert packet_in == disconnect_packet

        packet_in = fake_broker.receive_packet(1)
        assert not packet_in  # Check connection is closed

        fake_broker.finish()


if __name__ == '__main__':
    unittest.main()
