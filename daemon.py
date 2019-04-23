# coding: utf-8

import paho.mqtt.client as paho
import requests
import numpy
import json

chunk_divisor = 4


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

def on_connect(client, userdata, flags, rc):
    print("CONNACK received with code %d." % (rc))

    if rc == 0:
        print("Connected")
        client.subscribe("sensors/+/from_device")

def on_message(client, payload, msg):
    parts = msg.topic.split('/')
    data = json.loads(msg.payload.decode('utf-8'))

    chunk = find_chunk(
        data['pos']['lat'],
        data['pos']['lon'],
        chunk_divisor
    )

    if chunk:
        push_payload = {
            'from': parts[1],
            'pos': data['pos']
        }
        del data['pos']

        push_payload['data'] = data
        client.publish(
            'chunks/{0}/data'.format(hash(chunk)), 
            json.dumps(push_payload)
        )
        print('{0} | {1}'.format(
            hash(chunk), json.dumps(push_payload)
        ))

if __name__ == '__main__':
    client = paho.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.username_pw_set("rastadev", "rastadev")
    client.connect("vps505484.ovh.net", 1883)

    try:
        while True:
            client.loop()
    
    except KeyboardInterrupt:
        pass