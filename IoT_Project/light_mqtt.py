import RPi.GPIO as GPIO
from gpiozero import LED
import time
import paho.mqtt.client as mqtt

BROKER = '192.168.231.60'  # change as needed
PORT = 1883
TOPICS = ['Light']
USERNAME = 'mqtt'
PASSWORD = '1011project'

client = mqtt.Client()

client.username_pw_set(USERNAME, PASSWORD)


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print('Connected to MQTT Broker!')
    else:
        print('Failed to connect', rc)


def on_publish(client, userdata, mid):
    print('\nMessage Published\n')


client.on_connect = on_connect
client.on_publish = on_publish

client.connect(BROKER, PORT, 60)

client.loop_start()

GPIO.setmode(GPIO.BCM)
pin = 21
led = LED(17)

print("measuring light")

GPIO.setup(pin, GPIO.IN)

try:
    while True:
        light_detected = GPIO.input(pin)

        if light_detected == GPIO.HIGH:
            message = 'Light: Detected'
            led.off()


        else:
            message = 'Light: Not Detected'
            led.on()

        for topic in TOPICS:
            result = client.publish(topic, message)
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                print(f'Published message: {message} to topic: {topic}')
            else:
                print(f'Failed to send message to topic: {topic}')

        time.sleep(3)

except KeyboardInterrupt:
    print("Measurement stopped by user")
    GPIO.cleanup()

client.loop_stop()

client.disconnect()
