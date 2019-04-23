# coding: utf-8

import paho.mqtt.client as paho
import requests
import json

class CounterClient:

    def __init__(self, mqttArgs):
        self.client = paho.Client()
        self.buffer = {}
        
        def on_mc(c, u, f, r):
            nonlocal self
            self.on_connect(u,f, r)

        def on_mm(c, p, m):
            nonlocal self
            self.on_message(p, m)

        self.client.on_connect = on_mc
        self.client.on_message = on_mm
        self.client.username_pw_set(mqttArgs['username'], mqttArgs['password'])
        self.client.connect(mqttArgs['host'], mqttArgs['port'])
        self.connected = False
    
    def on_connect(self, userdata, flags, rc):
        if rc == 0:
            print('Connected')
            self.client.subscribe('chunks/+/data')
            self.connected = True

    def on_message(self, payload, msg):
        try:
            parts = msg.topic.split('/')
            data = json.loads(msg.payload.decode('utf-8'))

            current = self.buffer.get(data['from'], {})
            value = current.get(parts[1], 0)
            current[parts[1]] = value + 1
            self.buffer[data['from']] = current

        except Exception as ex:
            print(ex)


    def loop(self):
        self.client.loop()


if __name__ == '__main__':
    client = CounterClient(
        {
            'host': 'vps505484.ovh.net',
            'port': 1883,
            'username': 'vevedev',
            'password': 'vevedev'
        }
    )

    try:
        while True:
            client.loop()
            print(client.buffer)
    
    except KeyboardInterrupt:
        pass