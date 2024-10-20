import paho.mqtt.client as mqtt
import time

BROKER = '172.30.136.186'
PORT = 1883
TOPIC = 'test/topic'
USERNAME = 'mqtt'
PASSWORD = '1011project'

client = mqtt.Client(client_id="subscriber", clean_session=True)

client.username_pw_set(USERNAME, PASSWORD)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print('Connected to MQTT Broker!')
        client.subscribe(TOPIC)
        print(f'Subscribed to topic: {TOPIC}')
    else:
        print(f'Failed to connect, return code {rc}')

def on_message(client, userdata, msg):
    print(f'Received message: {msg.payload.decode()} from topic: {msg.topic}')

def on_subscribe(client, userdata, mid, granted_qos):
    print(f'Subscribed: {mid} {granted_qos}')

client.on_connect = on_connect
client.on_message = on_message
client.on_subscribe = on_subscribe

client.connect(BROKER, PORT, 60)

client.loop_start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Exiting...")
finally:
    client.loop_stop()
    client.disconnect()

