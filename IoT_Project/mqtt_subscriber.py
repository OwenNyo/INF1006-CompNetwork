import RPi.GPIO as GPIO
import time
from paho.mqtt import client as mqtt_client

broker_address = "test.mosquitto.org"
port=1883
client1 = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION1, "client")
client1.connect(broker_address,port)

BUZZER = 17
GREENLED = 27
REDLED = 22
BUTTON = 11
LCD_RS = 5
LCD_E  = 6
LCD_D4 = 19
LCD_D5 = 26
LCD_D6 = 13
LCD_D7 = 16
LCD_WIDTH = 16    # Maximum characters per line
LCD_CHR = True
LCD_CMD = False
LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line
E_PULSE = 0.0005
E_DELAY = 0.0005
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)       # Use BCM GPIO numbers
GPIO.setup(BUZZER, GPIO.OUT)
GPIO.setup(GREENLED, GPIO.OUT)
GPIO.setup(REDLED, GPIO.OUT)
GPIO.setup(BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(LCD_E, GPIO.OUT)  # E
GPIO.setup(LCD_RS, GPIO.OUT) # RS
GPIO.setup(LCD_D4, GPIO.OUT) # DB4
GPIO.setup(LCD_D5, GPIO.OUT) # DB5
GPIO.setup(LCD_D6, GPIO.OUT) # DB6
GPIO.setup(LCD_D7, GPIO.OUT) # DB7
x = 0
mode = 0
previousPrice = 0
crypto = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT']

def main():
    global x,mode
    GPIO.add_event_detect(BUTTON, GPIO.FALLING, callback=myInterrupt, bouncetime=100)
    setupMQTT(x)
    while True:
        if mode == 1:
            GPIO.output(GREENLED, True)
            GPIO.output(REDLED, False)
            GPIO.output(BUZZER, False)
        elif mode == 2:
            GPIO.output(GREENLED, False)
            GPIO.output(REDLED, True)
            GPIO.output(BUZZER, True)
        else:
            GPIO.output(GREENLED, False)
            GPIO.output(REDLED, False)
            GPIO.output(BUZZER, False)
        #print('hello' + str(x))

def myInterrupt(channel):
    global x
    start_time = time.time()
    while GPIO.input(channel) == 0:
        pass
    buttonTime = time.time()-start_time
    if buttonTime > 0.1:
    #if .1 <= buttonTime < 4:
        print('Button Pressed')
        client1.unsubscribe(f"yaohao/crypto/"+crypto[x])
        x = changeSymbol()
        setupMQTT(x)

    #elif buttonTime >= 4:
        #lcd_display(0x01, LCD_CMD)
        #lcd_string('Shutting down...',LCD_LINE_1)
        #time.sleep(3)

def setupMQTT(symbol):
    topic = f"yaohao/crypto/"+crypto[symbol]
    print(topic)
    client1.subscribe(topic)
    client1.on_message = on_message

def on_message(client, userdata, message):
    global mode, previousPrice
    msg = message.payload.decode().split(' ')
    lcd_string(msg[0],LCD_LINE_1)
    lcd_string(msg[1],LCD_LINE_2)
    currentPrice = float(msg[1].replace('$',''))
    if currentPrice > previousPrice:
        mode = 1
    elif previousPrice > currentPrice:
        mode = 2
    else:
        mode = 0
    previousPrice = currentPrice
    print(f"Received message '{message.payload.decode()}' on topic '{message.topic}'")

def changeSymbol():
    global x, mode, previousPrice
    time.sleep(0.1)
    mode = 0
    previousPrice = 0
    if x == 2:
        x = 0
    else:
        x = x + 1
    lcd_string('Now Watching:   ',LCD_LINE_1)
    lcd_string(crypto[x],LCD_LINE_2)
    time.sleep(1)
    return x

def lcd_init():
  lcd_display(0x28,LCD_CMD) # Selecting 4 - bit mode with two rows
  lcd_display(0x0C,LCD_CMD) # Display On,Cursor Off, Blink Off
  lcd_display(0x01,LCD_CMD) # Clear display
  time.sleep(E_DELAY)

def lcd_display(bits, mode):
  GPIO.output(LCD_RS, mode) # RS
  GPIO.output(LCD_D4, False)
  GPIO.output(LCD_D5, False)
  GPIO.output(LCD_D6, False)
  GPIO.output(LCD_D7, False)
  if bits&0x10==0x10:
    GPIO.output(LCD_D4, True)
  if bits&0x20==0x20:
    GPIO.output(LCD_D5, True)
  if bits&0x40==0x40:
    GPIO.output(LCD_D6, True)
  if bits&0x80==0x80:
    GPIO.output(LCD_D7, True)
  # Toggle 'Enable' pin
  lcd_toggle_enable()
  GPIO.output(LCD_D4, False)
  GPIO.output(LCD_D5, False)
  GPIO.output(LCD_D6, False)
  GPIO.output(LCD_D7, False)
  if bits&0x01==0x01:
    GPIO.output(LCD_D4, True)
  if bits&0x02==0x02:
    GPIO.output(LCD_D5, True)
  if bits&0x04==0x04:
    GPIO.output(LCD_D6, True)
  if bits&0x08==0x08:
    GPIO.output(LCD_D7, True)
  lcd_toggle_enable()

def lcd_toggle_enable():
  time.sleep(E_DELAY)
  GPIO.output(LCD_E, True)
  time.sleep(E_PULSE)
  GPIO.output(LCD_E, False)
  time.sleep(E_DELAY)

def lcd_string(message,line):
  message = message.ljust(LCD_WIDTH," ")
  lcd_display(line, LCD_CMD)
  for i in range(LCD_WIDTH):
    lcd_display(ord(message[i]),LCD_CHR)

if __name__ == '__main__':
  try:
      lcd_init()
      lcd_string('Welcome to',LCD_LINE_1)
      lcd_string('CryptoAlert!',LCD_LINE_2)
      client1.loop_start()
      time.sleep(1)
      main()
  except KeyboardInterrupt:
      pass
  finally:
      lcd_display(0x01, LCD_CMD)
      GPIO.cleanup()
      client1.disconnect
      client1.loop_stop()