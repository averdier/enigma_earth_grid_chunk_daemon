# coding: utf-8

import time
import json
import paho.mqtt.client as paho

payload = {
    'kind': 'ping:devices'
}

def on_connect(client, userdata, flags, rc):
    print("CONNACK received with code %d." % (rc))

    if rc == 0:
        print("Connected")
        client.subscribe('chunks/+/devices')
        client.publish('chunks/8324716771535245060/from_clients', json.dumps(payload))

def on_message(client, payload, msg):
    data = json.loads(msg.payload.decode('utf-8'))
    print(data)

if __name__ == '__main__':
    client = paho.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.username_pw_set("chunk_counter", "chunk_counter")
    client.connect("vps505484.ovh.net", 1883)

    try:
        while True:
            client.loop()
                

    except KeyboardInterrupt:
        pass

    
