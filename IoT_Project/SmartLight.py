from PyP100 import PyP100

p100 = PyP100.P100("172.20.10.2", "dontdotis@gmail.com", "NZY1006smartplug") #Creates a P100 plug object

p100.handshake() #Creates the cookies required for further methods
p100.login() #Sends credentials to the plug and creates AES Key and IV for further methods

p100.turnOn() #Turns the connected plug on
# p100.turnOff() #Turns the connected plug off
# p100.toggleState() #Toggles the state of the connected plug

# p100.turnOnWithDelay(10) #Turns the connected plug on after 10 seconds
# p100.turnOffWithDelay(10) #Turns the connected plug off after 10 seconds