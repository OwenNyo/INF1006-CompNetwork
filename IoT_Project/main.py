import base64
from io import BytesIO
from flask import Flask, render_template
import paho.mqtt.client as mqtt
from flask_socketio import SocketIO, emit
import csv
import os
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import time
import threading  # Import threading module for multithreading
from PyP100 import PyP100
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app)

# CSV File Paths
LIGHT_FILE = 'static/csv/Light.csv'
MOTION_FILE = 'static/csv/Motion.csv'
TEMPERATURE_FILE = 'static/csv/Temperature.csv'
ULTRASONIC_FILE = 'static/csv/Ultrasonic.csv'

# MQTT Broker Settings
BROKER = '192.168.1.30'
PORT = 1883
TOPICS = ['Motion', 'Ultrasonic', 'Light', 'Temperature,Humidity']
USERNAME = 'mqtt'
PASSWORD = '1011project'

p100 = PyP100.P100("192.168.1.8", "dontdotis@gmail.com", "NZY1006smartplug") #Creates a P100 plug object

p100v2 = PyP100.P100("192.168.1.14", "idkwhattoput30@gmail.com", "mqtt1011smartplug") #Creates a P100 plug object

p100.handshake() #Creates the cookies required for further methods
p100.login() #Sends credentials to the plug and creates AES Key and IV for further methods
last_motion_time = time.time()

def control_device(device, motion):
    global last_motion_time
    current_time = time.time()

    # Check if motion is detected
    if motion == "Detected":
        device.turnOn()
        last_motion_time = current_time
    elif motion == "Not Detected":
        # Check if 10 seconds have passed since the last motion detection
        if current_time - last_motion_time >= 5:
            device.turnOff()


# Function to read latest data and emit it to clients
def emit_latest_data():
    TemperatureAndHumidity = read_latest_from_csv(TEMPERATURE_FILE, limit=1)
    Motion = read_latest_from_csv(MOTION_FILE, limit=1)
    Ultrasonic = read_latest_from_csv(ULTRASONIC_FILE, limit=1)
    Light = read_latest_from_csv(LIGHT_FILE, limit=1)
    socketio.emit('update_data', {
        'TemperatureAndHumidity': TemperatureAndHumidity,
        'Motion': Motion,
        'Ultrasonic': Ultrasonic,
        'Light': Light
    }, namespace='/')

# On Connect / Message Callbacks
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print('Connected to MQTT Broker!')
        for topic in TOPICS:
            client.subscribe(topic)
            print(f'Subscribed to topic: {topic}')
    else:
        print(f'Failed to connect, return code {rc}')

def on_message(client, userdata, msg):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(msg.topic, msg.payload.decode())
    # Check topic keywords for specific processing
    if 'temperature' in msg.topic.lower():
        write_to_csv(msg.topic, msg.payload.decode(), timestamp, TEMPERATURE_FILE)
        control_device(p100v2, msg.payload.decode())
    elif 'motion' in msg.topic.lower():
        write_to_csv(msg.topic, msg.payload.decode(), timestamp, MOTION_FILE)
        control_device(p100v2, msg.payload.decode())
    elif 'light' in msg.topic.lower():
        write_to_csv(msg.topic, msg.payload.decode(), timestamp, LIGHT_FILE)
    elif 'ultrasonic' in msg.topic.lower():
        write_to_csv(msg.topic, msg.payload.decode(), timestamp, ULTRASONIC_FILE)
    else:
        print('Topic not found!')
    
    emit_latest_data()
    
# Setting up Client Connection
client = mqtt.Client(client_id="subscriber", clean_session=True)
client.username_pw_set(USERNAME, PASSWORD)
client.on_connect = on_connect
client.on_message = on_message
client.connect(BROKER, PORT, 60)
client.loop_start()

# Function to write message to CSV file
def write_to_csv(topic, payload, timestamp, CSV_FILE):
    is_file_empty = os.stat(CSV_FILE).st_size == 0
    with open(CSV_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        if is_file_empty:
            writer.writerow(['Timestamp', 'Topic', 'Message'])
        writer.writerow([timestamp, topic, payload])

# Function to read the latest message from CSV file
def read_latest_from_csv(CSV_FILE, limit=1):
    messages = []
    try:
        with open(CSV_FILE, mode='r', newline='') as file:
            reader = csv.DictReader(file)
            rows = list(reader)
            # Determine where to start reading from (handle case where there are fewer than 'limit' rows)
            start_index = max(0, len(rows) - limit)
            for row in rows[start_index:]:
                message = {
                    'timestamp': row['Timestamp'],
                    'topic': row['Topic'],
                    'message': row['Message']
                }
                messages.append(message)
    except FileNotFoundError:
        # Handle if file does not exist initially
        pass
    return messages

@app.route('/')
def home():
    Temperature = read_latest_from_csv(TEMPERATURE_FILE, limit=1)
    Motion = read_latest_from_csv(MOTION_FILE, limit=1)
    Ultrasonic = read_latest_from_csv(ULTRASONIC_FILE, limit=1)
    Light = read_latest_from_csv(LIGHT_FILE, limit=1)
    return render_template('index.html', Temperature=Temperature,
                           Motion=Motion, Ultrasonic=Ultrasonic, Light=Light)

@app.route('/graphs')
def graphs():
    # Read CSV into DataFrame
    df = pd.read_csv(TEMPERATURE_FILE)

    # Split 'Message' column into 'Temperature' and 'Humidity' columns
    df[['Temperature', 'Humidity']] = df['Message'].str.split(',', expand=True)

    # Convert 'Timestamp' column to datetime format
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], format='%Y-%m-%d %H:%M:%S')

    # Convert 'Temperature' and 'Humidity' columns to numeric types
    df['Temperature'] = pd.to_numeric(df['Temperature'])
    df['Humidity'] = pd.to_numeric(df['Humidity'])

    # Create separate DataFrames for Temperature and Humidity
    df_temperature = df[['Timestamp', 'Temperature']].set_index('Timestamp')
    df_temperature = df_temperature.resample('5T').mean().reset_index()
    df_humidity = df[['Timestamp', 'Humidity']].set_index('Timestamp')
    df_humidity = df_humidity.resample('5T').mean().reset_index()

    # Plotting Temperature
    plt.figure(figsize=(8, 5))
    plt.plot(df_temperature['Timestamp'], df_temperature['Temperature'], marker='o', linestyle='-', color='b')
    plt.title('Temperature Over Time')
    plt.xlabel('Timestamp')
    plt.ylabel('Temperature (°C)')
    plt.grid(True)
    plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%Y-%m-%d %H:%M'))
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Convert plot to PNG image and encode it
    img_temperature = BytesIO()
    plt.savefig(img_temperature, format='png')
    img_temperature.seek(0)
    plot_url_temperature = base64.b64encode(img_temperature.getvalue()).decode()

    # Plotting Humidity
    plt.figure(figsize=(8, 5))
    plt.plot(df_humidity['Timestamp'], df_humidity['Humidity'], marker='o', linestyle='-', color='g')
    plt.title('Humidity Over Time')
    plt.xlabel('Timestamp')
    plt.ylabel('Humidity (%)')
    plt.grid(True)
    plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%Y-%m-%d %H:%M'))
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Convert plot to PNG image and encode it
    img_humidity = BytesIO()
    plt.savefig(img_humidity, format='png')
    img_humidity.seek(0)
    plot_url_humidity = base64.b64encode(img_humidity.getvalue()).decode()

    return render_template('graphs.html', temperature=plot_url_temperature, humidity=plot_url_humidity)

if __name__ == '__main__':
    # Start Flask SocketIO application
    socketio.run(app, debug=True, use_reloader=False, allow_unsafe_werkzeug=True)
