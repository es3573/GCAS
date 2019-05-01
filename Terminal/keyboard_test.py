"""
Created on Thu Apr 25 09:58:50 2019

@author: eriksu
"""

import paho.mqtt.client as mqtt
import keyboard

# Defines
NO_MOTION = 0
LEFT_SWIPE = 1
RIGHT_SWIPE = 2
UP_SWIPE = 3
DOWN_SWIPE = 4

broker_address = '192.168.0.24'
topic = "topic/gcas/prediction"

# Local Functions
# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    client.subscribe(topic)
    print('\n\rSubscribed to' + topic)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    payload = msg.payload
    process_prediction(payload)
    
# Based off Prediction value, do something
def process_prediction(payload):
    action = int(payload)
    if action == NO_MOTION:
        keyboard.write('No motion detected')
        keyboard.press('enter')
    if action == LEFT_SWIPE:
        keyboard.press_and_release('down')
    elif action == RIGHT_SWIPE:
        keyboard.press_and_release('up')

# MAIN
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
print("Connecting to MQTT . . . ")
if(mqtt_client.connect(broker_address) == 0):
    mqtt_client.loop_start()
while True:
    pass

    

