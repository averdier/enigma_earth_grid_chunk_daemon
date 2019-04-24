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
        self.devices_chunk = {}
        self.chunks_devices = {}

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
            self.client.subscribe(self.config.CHUNKS_WILDCARD)
            self.logger.info('subscribed to {0}'.format(self.config.CHUNKS_WILDCARD))

    def on_message(self, payload, msg):
        parts = msg.topic.split('/')
        data = json.loads(msg.payload.decode('utf-8'))

        if 'sensors' in parts:
            self.on_device_data(parts[1], data)
        
        if 'chunks' in parts and 'from_clients' in parts:
            self.on_command(parts[1], data['kind'])
        
    def on_command(self, chunk, command):
        if command == 'ping:devices':
            self.update_chunk_device_list(chunk)
        
    
    def on_device_data(self, deviceId, data):
        chunk = find_chunk(
            data['pos']['lat'],
            data['pos']['lon'],
            self.config.CHUNK_DIVISOR
        )

        if chunk:
            push_payload = {
                'from': deviceId,
                'pos': data['pos']
            }
            del data['pos']

            chunk_hash = str(hash(chunk))

            push_payload['data'] = data
            self.client.publish(
                'chunks/{0}/data'.format(chunk_hash), 
                json.dumps(push_payload)
            )
            self.logger.debug('data send')

            self.update_chunk_device_event(deviceId, chunk_hash)

    def update_chunk_device_event(self, deviceId, currentChunk):
        old_device_chunk = self.devices_chunk.get(deviceId, '')
        if old_device_chunk != currentChunk:
            if old_device_chunk != '':
                self.chunks_devices[old_device_chunk].remove(deviceId)
                self.client.publish(
                'chunks/{0}/events'.format(old_device_chunk),
                    json.dumps({
                        'kind': 'device:exited',
                        'args': {
                            'deviceId': deviceId
                        }
                    })
                )
                self.logger.debug('exit event send')
                self.update_chunk_device_list(old_device_chunk)

            if self.chunks_devices.get(currentChunk):
                self.chunks_devices[currentChunk].append(deviceId)
            else:
                self.chunks_devices[currentChunk] = [deviceId]

            self.client.publish(
                'chunks/{0}/events'.format(currentChunk),
                json.dumps({
                    'kind': 'device:entered',
                    'args': {
                        'deviceId': deviceId
                    }
                })
            )
            self.devices_chunk[deviceId] = currentChunk
            self.logger.debug('enter event send')
            self.update_chunk_device_list(currentChunk)
        
    def update_chunk_device_list(self, chunk):
        self.client.publish(
            'chunks/{0}/devices'.format(chunk),
            json.dumps(self.chunks_devices.get(chunk, []))
        )

    def loop(self):
        self.client.loop()