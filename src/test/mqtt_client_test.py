import unittest

import _thread
import pytest
import unicodedata

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

        mqttc.loop_stop()
        fake_broker.finish()

    def test_connect_failure(self):
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

        connack_packet = paho_test.gen_connack(rc=1)
        count = fake_broker.send_packet(connack_packet)
        assert count  # Check connection was not closed
        assert count == len(connack_packet)

        packet_in = fake_broker.receive_packet(1)
        assert not packet_in  # Check connection is closed

        mqttc.loop_stop()
        fake_broker.finish()


class TestPublishBrokerToClient(unittest.TestCase):

    def test_invalid_utf8_topic(self):
        mqttc = MqttHandler(client_id=CLIENT_ID, topic='test_topic', broker_host='localhost', broker_port=1888)

        def on_message(client, userdata, msg):
            with pytest.raises(UnicodeDecodeError):
                msg.topic
            client.disconnect()

        mqttc.client.on_message = on_message

        mqttc.connect_async()
        mqttc.loop_start()

        try:
            fake_broker = FakeBroker()
            fake_broker.start()

            connect_packet = paho_test.gen_connect(CLIENT_ID)
            packet_in = fake_broker.receive_packet(len(connect_packet))
            assert packet_in  # Check connection was not closed
            assert packet_in == connect_packet

            connack_packet = paho_test.gen_connack(rc=0)
            count = fake_broker.send_packet(connack_packet)
            assert count  # Check connection was not closed
            assert count == len(connack_packet)

            publish_packet = paho_test.gen_publish(b"\xff", qos=0)
            count = fake_broker.send_packet(publish_packet)
            assert count  # Check connection was not closed
            assert count == len(publish_packet)

            mqttc.disconnect()
            disconnect_packet = paho_test.gen_disconnect()
            packet_in = fake_broker.receive_packet(len(disconnect_packet))
            assert packet_in  # Check connection was not closed
            assert packet_in == disconnect_packet

        finally:
            mqttc.loop_stop()

        packet_in = fake_broker.receive_packet(1)
        assert not packet_in  # Check connection is closed

        fake_broker.finish()

    def test_valid_utf8_topic_recv(self):
        mqttc = MqttHandler(client_id=CLIENT_ID, topic='test_topic', broker_host='localhost', broker_port=1888)

        # It should be non-ascii multi-bytes character
        topic = unicodedata.lookup('SNOWMAN')

        def on_message(client, userdata, msg):
            assert msg.topic == topic
            client.disconnect()

        mqttc.client.on_message = on_message

        mqttc.connect_async()
        mqttc.loop_start()

        try:
            fake_broker = FakeBroker()
            fake_broker.start()

            connect_packet = paho_test.gen_connect(CLIENT_ID)
            packet_in = fake_broker.receive_packet(len(connect_packet))
            assert packet_in  # Check connection was not closed
            assert packet_in == connect_packet

            connack_packet = paho_test.gen_connack(rc=0)
            count = fake_broker.send_packet(connack_packet)
            assert count  # Check connection was not closed
            assert count == len(connack_packet)

            publish_packet = paho_test.gen_publish(
                topic.encode('utf-8'), qos=0
            )
            count = fake_broker.send_packet(publish_packet)
            assert count  # Check connection was not closed
            assert count == len(publish_packet)

            mqttc.disconnect()
            disconnect_packet = paho_test.gen_disconnect()
            packet_in = fake_broker.receive_packet(len(disconnect_packet))
            assert packet_in  # Check connection was not closed
            assert packet_in == disconnect_packet

        finally:
            mqttc.loop_stop()

        packet_in = fake_broker.receive_packet(1)
        assert not packet_in  # Check connection is closed

        fake_broker.finish()

    def test_publish_single_message(self):

        topic = 'test_topic'
        payload = 'message'

        def publish_message():
            MqttHandler.publish_single_message(topic=topic, payload=payload,
                                               hostname='localhost', port=1888,
                                               client_id=CLIENT_ID)

        _thread.start_new_thread(publish_message, ())

        fake_broker = FakeBroker()
        fake_broker.start()

        connect_packet = paho_test.gen_connect(CLIENT_ID)
        packet_in = fake_broker.receive_packet(len(connect_packet))
        assert packet_in  # Check connection was not closed
        assert packet_in == connect_packet

        connack_packet = paho_test.gen_connack(rc=0)
        count = fake_broker.send_packet(connack_packet)
        assert count  # Check connection was not closed
        assert count == len(connack_packet)

        publish_packet = paho_test.gen_publish(
            topic=topic, payload=str.encode(payload), qos=0
        )

        packet_in = fake_broker.receive_packet(len(publish_packet))
        assert packet_in  # Check connection was not closed
        self.assertEqual(packet_in, publish_packet)

        fake_broker.finish()


if __name__ == '__main__':
    unittest.main()
