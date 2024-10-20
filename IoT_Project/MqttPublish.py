import paho.mqtt.client as mqtt
import time

BROKER = '192.168.183.162'
PORT = 1883
TOPICS = ['Motion', 'test/topic1']
USERNAME = 'mqtt'
PASSWORD = '1011project'

client = mqtt.Client()

client.username_pw_set(USERNAME, PASSWORD)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print('Connected to MQTT Broker!')
    else:
        print('Failed to connect', rc)

def on_publish(client,userdata,mid):
    print('Message Published')

client.on_connect = on_connect
client.on_publish = on_publish

client.connect(BROKER, PORT, 60)

client.loop_start()

try:
    count = 1
    while True:
        message = f'Detected'

        for topic in TOPICS:
            result = client.publish(topic, message)
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                print(f'Published message: {message} to topic: {topic}')
            else:
                print(f'Failed to send message to topic: {topic}')
        
        count += 1

        time.sleep(1000)

except KeyboardInterrupt:
    print('Exiting...')

client.loop_stop()

client.disconnect()





