# coding: utf-8

import time
import json
import paho.mqtt.client as paho

payload = {
    'humidty': 1,
    'temperature': 1,
    'heat_index': 1,
    'pos': {
        'lat': 50.629874,
        'lon': 3.055467
    }
}

def on_connect(client, userdata, flags, rc):
    print("CONNACK received with code %d." % (rc))

    if rc == 0:
        print("Connected")

if __name__ == '__main__':
    client = paho.Client()
    client.on_connect = on_connect
    client.username_pw_set("vevedev", "vevedev")
    client.connect("vps505484.ovh.net", 1883)

    try:
        while True:
            client.loop()
            result = client.publish('sensors/dev/from_device', json.dumps(payload))
            time.sleep(2)
                

    except KeyboardInterrupt:
        pass

    
