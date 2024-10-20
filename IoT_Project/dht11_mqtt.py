import RPi.GPIO as GPIO
import time
import paho.mqtt.client as mqtt
import adafruit_dht
import board


#requires additional installation and configuration for adafruit
BROKER = '192.168.183.162' #change as needed
PORT = 1883
TOPICS = ['Temperature,Humidity']
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

dht_device = adafruit_dht.DHT11(board.D4)
    
while True:
    try:
     
       temperature_c = dht_device.temperature
       temperature_f = temperature_c * (9/5) + 32
       humidity = dht_device.humidity
       """
       temperature_c = 1
       temperature_f = 2
       humidity = 3
       """
       print("Temp:{} C / {} F Humidity: {}%".format(temperature_c,temperature_f,humidity))
       
       message = f'{temperature_c},{humidity}'
       #To test on MQTT broker for temperature and humidity   
       #message = f'{temperature_c},{humidity}'
       for topic in TOPICS:
               result = client.publish(topic, message)
               if result.rc == mqtt.MQTT_ERR_SUCCESS:
                   print(f'Published message: {message} to topic: {topic}')
               else:
                   print(f'Failed to send message to topic: {topic}')             
           
    except RuntimeError as err:
       print(err.args[0])
    time.sleep(2.0)
    
client.loop_stop()

client.disconnect()

