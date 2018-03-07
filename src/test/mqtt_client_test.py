import _thread
import unicodedata
import unittest

import pytest

from core.mqtt_handler import MqttHandler
from test.paho_mqtt_test_helper import paho_test
from test.paho_mqtt_test_helper.broker import FakeBroker

CLIENT_ID = 'test_connection_client'


class TestConnection(unittest.TestCase):

    def test_connect_success(self):
        mqttc = make_active_client()

        fake_broker = FakeBroker()
        fake_broker.start()

        check_connection_established(fake_broker)

        check_connection_ack(fake_broker)

        mqttc.disconnect()
        disconnect_packet = paho_test.gen_disconnect()
        packet_in = fake_broker.receive_packet(len(disconnect_packet))
        assert packet_in  # Check connection was not closed
        assert packet_in == disconnect_packet

        packet_in = fake_broker.receive_packet(1)
        assert not packet_in  # Check connection is closed

        mqttc.loop_stop()
        fake_broker.finish()

    def test_connect_failure(self):
        mqttc = make_active_client()

        fake_broker = FakeBroker()
        fake_broker.start()

        check_connection_established(fake_broker)

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
        mqttc = make_active_client()

        def on_message(client, userdata, msg):
            with pytest.raises(UnicodeDecodeError):
                print(msg.topic)

        mqttc.client.on_message = on_message

        try:
            fake_broker = FakeBroker()
            fake_broker.start()

            check_connection_established(fake_broker)

            check_connection_ack(fake_broker)

            publish_packet = paho_test.gen_publish(b"\xff", qos=0)
            count = fake_broker.send_packet(publish_packet)
            assert count  # Check connection was not closed
            assert count == len(publish_packet)

        finally:
            mqttc.loop_stop()
            mqttc.disconnect()

        fake_broker.finish()

    def test_valid_utf8_topic_recv(self):
        mqttc = make_active_client()

        # It should be non-ascii multi-bytes character
        topic = unicodedata.lookup('SNOWMAN')

        def on_message(client, userdata, msg):
            assert msg.topic == topic

        mqttc.client.on_message = on_message

        try:
            fake_broker = FakeBroker()
            fake_broker.start()

            check_connection_established(fake_broker)

            check_connection_ack(fake_broker)

            publish_packet = paho_test.gen_publish(
                topic.encode('utf-8'), qos=0
            )
            count = fake_broker.send_packet(publish_packet)
            assert count  # Check connection was not closed
            assert count == len(publish_packet)

        finally:
            mqttc.loop_stop()
            mqttc.disconnect()

        fake_broker.finish()

    def test_message_callback(self):
        topic = 'test_topic'
        payload = '{"command":"set_data_rate","args":[10]}'

        mqttc = make_active_client()

        try:
            fake_broker = FakeBroker()
            fake_broker.start()

            check_connection_established(fake_broker)

            check_connection_ack(fake_broker)

            publish_packet = paho_test.gen_publish(
                topic=topic, payload=str.encode(payload), qos=0
            )
            count = fake_broker.send_packet(publish_packet)
            assert count  # Check connection was not closed
            assert count == len(publish_packet)

        finally:
            mqttc.loop_stop()
            mqttc.disconnect()

        fake_broker.finish()


class TestPublishClientToBroker(unittest.TestCase):
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

        check_connection_established(fake_broker)

        check_connection_ack(fake_broker)

        publish_packet = paho_test.gen_publish(
            topic=topic, payload=str.encode(payload), qos=0
        )

        packet_in = fake_broker.receive_packet(len(publish_packet))
        assert packet_in  # Check connection was not closed
        self.assertEqual(packet_in, publish_packet)

        fake_broker.finish()


def make_active_client():
    mqttc = MqttHandler(client_id=CLIENT_ID, topic='test_topic', broker_host='localhost', broker_port=1888)
    mqttc.connect_async()
    mqttc.loop_start()
    return mqttc


def check_connection_established(fake_broker):
    connect_packet = paho_test.gen_connect(CLIENT_ID)
    packet_in = fake_broker.receive_packet(len(connect_packet))
    assert packet_in  # Check connection was not closed
    assert packet_in == connect_packet


def check_connection_ack(fake_broker):
    connack_packet = paho_test.gen_connack(rc=0)
    count = fake_broker.send_packet(connack_packet)
    assert count  # Check connection was not closed
    assert count == len(connack_packet)


if __name__ == '__main__':
    unittest.main()
