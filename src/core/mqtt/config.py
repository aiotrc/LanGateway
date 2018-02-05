"""
Global variables
"""
import os

# 172.23.132.37
broker_address = os.getenv('MQTT_BROKER', 'iot.eclipse.org')
broker_port = 1883

message_topic = 'lan_gateway_topic'
client_name = 'lan_gateway'
publish_name = 'lan_gateway'
