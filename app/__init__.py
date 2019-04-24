# coding: utf-8

import logging
import paho.mqtt.client as paho
import requests
import numpy
import json
from config import config


def find_chunk(lat, lon, parts):
    previous_lat = int(lat)
    increment = 1 / parts

    for i in numpy.arange(previous_lat + increment, previous_lat + 1, increment):

        previous_lon = int(lon)
        for j in numpy.arange(previous_lon + increment, previous_lon + 1, increment):
            if previous_lat <= lat <= i and previous_lon <= lon <= j:
                return (i,j)
            previous_lon = j
        previous_lat = i

    return None


class BaseApp:
    def __init__(self, config_name):
        self.logger = logging.getLogger(__name__)
        self.config = config[config_name]
        config[config_name].init_app(self)
        self.logger.setLevel(logging.DEBUG)


class ChunkDaemon(BaseApp):

    def __init__(self, config_name):
        super().__init__(config_name)
        self.client = paho.Client()

        def on_mqtt_connect(client, userdata, flags, rc):
            nonlocal self
            self.on_connect(userdata, flags, rc)
        
        def on_mqtt_message(client, payload, msg):
            nonlocal self
            self.on_message(payload, msg)

        self.client.on_connect = on_mqtt_connect
        self.client.on_message = on_mqtt_message
        self.client.username_pw_set(self.config.BROKER_USERNAME, self.config.BROKER_PASSWORD)
        self.client.connect(self.config.BROKER_HOST, self.config.BROKER_PORT)
        self.connected = False

    def on_connect(self, userdata, flags, rc):
        self.logger.debug('connack: {0}'.format(rc))
        if rc == 0:
            self.connected = True
            self.logger.info('connected')
            self.client.subscribe(self.config.DEVICES_WILDCARD)
            self.logger.info('subscribed to {0}'.format(self.config.DEVICES_WILDCARD))

    def on_message(self, payload, msg):
        parts = msg.topic.split('/')
        data = json.loads(msg.payload.decode('utf-8'))

        chunk = find_chunk(
            data['pos']['lat'],
            data['pos']['lon'],
            self.config.CHUNK_DIVISOR
        )

        if chunk:
            push_payload = {
                'from': parts[1],
                'pos': data['pos']
            }
            del data['pos']

            push_payload['data'] = data
            self.client.publish(
                'chunks/{0}/data'.format(hash(chunk)), 
                json.dumps(push_payload)
            )

    def loop(self):
        self.client.loop()