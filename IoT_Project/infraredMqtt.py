import RPi.GPIO as GPIO
import time
import paho.mqtt.client as mqtt

# GPIO setup
PIR_PIN = 27
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIR_PIN, GPIO.IN)

# MQTT setup
BROKER = '192.168.183.162'
PORT = 1883
TOPIC = 'Motion'
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
    print('Message Published')

client.on_connect = on_connect
client.on_publish = on_publish

client.connect(BROKER, PORT, 60)
client.loop_start()

print('PIR SENSOR TEST')
time.sleep(2)
print('Ready')

# Sensitivity control variables
detection_threshold = 3  # Number of consecutive detections to confirm motion
detection_count = 0      # Counter for consecutive detections
no_motion_count = 0      # Counter for consecutive no motion detections
no_motion_threshold = 3  # Number of consecutive no motion to reset detection count

try:
    while True:
        if GPIO.input(PIR_PIN):
            detection_count += 1
            no_motion_count = 0
            if detection_count >= detection_threshold:
                message = 'Detected'
                result = client.publish(TOPIC, message)
                status = result.rc
                if status == 0:
                    print(f': {message} to topic: {TOPIC} \n')
                else:
                    print('Failed to send message to topic')
                detection_count = 0  # Reset detection count after publishing
        else:
            no_motion_count += 1
            if no_motion_count >= no_motion_threshold:
                detection_count = 0  # Reset detection count if no motion is detected for a while
            message = 'Not Detected'
            result = client.publish(TOPIC, message)
            status = result.rc
            if status == 0:
                print(f': {message} to topic: {TOPIC} \n')
            else:
                print('Failed to send message to topic')
        time.sleep(3)
except KeyboardInterrupt:
    print('QUIT')
finally:
    GPIO.cleanup()
    client.loop_stop()
    client.disconnect()

