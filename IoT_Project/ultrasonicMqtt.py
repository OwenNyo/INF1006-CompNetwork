import RPi.GPIO as GPIO
import time
import paho.mqtt.client as mqtt
import time

BROKER = '192.168.183.162' #change as needed
PORT = 1883
TOPICS = ['Ultrasonic']
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
    print('\nMessage Published\n')

client.on_connect = on_connect
client.on_publish = on_publish

client.connect(BROKER, PORT, 60)

client.loop_start()


GPIO.setmode(GPIO.BCM)

TRIG = 23
ECHO = 24

print("Distance Measurement In Progress")

GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

try:	
    while True:
        GPIO.output(TRIG, False)
        time.sleep(0.2)  
        
        GPIO.output(TRIG, True)
        time.sleep(0.00001) 
        GPIO.output(TRIG, False)
        
        while GPIO.input(ECHO) == 0:
            pulse_start = time.time()
        
        while GPIO.input(ECHO) == 1:
            pulse_end = time.time()

        pulse_duration = pulse_end - pulse_start
        
        distance = pulse_duration * 17150
        distance = round(distance, 2)
        
        message = f'{distance}'
        
        for topic in TOPICS:
            result = client.publish(topic, message)
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                print(f'Published message: {message} to topic: {topic}')
            else:
                print(f'Failed to send message to topic: {topic}')
        
        time.sleep(1)

except KeyboardInterrupt:
    print("Measurement stopped by user")
    GPIO.cleanup()
    
client.loop_stop()

client.disconnect()
