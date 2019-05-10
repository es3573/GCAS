# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django_tables2 import RequestConfig

from .models import GCAS
from .tables import GCASTable

import paho.mqtt.client as mqtt
import mraa
import math
import time

# Defines
NO_MOTION = 0
RIGHT_SWIPE = 1
LEFT_SWIPE = 2
DOUBLE_TAP = 3
WAVE = 4

# home
#broker_address = '192.168.0.24'
# pigeon
#broker_address = '192.168.2.143'
# columbia
broker_address = '192.168.0.215'
downlink_topic = "topic/gcas/prediction"

# Local Functions
# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    client.subscribe(downlink_topic)
    print('\n\rSubscribed to' + downlink_topic)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    payload = msg.payload
    data = GCAS()
    data.prediction = int(payload)
    process_prediction(payload, data)

# convert temperature
def convert_temp(raw_data):
    R0 = 100000
    B = 4275
    R = 1023.0/(raw_data)-1.0;
    R = R0*R
    temperature = 1.0/(math.log(R/R0)/B+1/298.15)-273.15
    return temperature

# reset LEDs
def reset_LEDs():
    red_led.write(0)
    green_led.write(0)
    blue_led.write(0)
    
# process prediction for action
def process_prediction(payload, data):
    action = int(payload)
    reset_LEDs()
    if action == NO_MOTION:
        current_temp = convert_temp(tempSensor.read())
        data.temperature = current_temp
        data.action = 'NO MOTION'
        data.expected = 'keyboard write'
        data.save()
    elif action == LEFT_SWIPE:
        data.action = 'LEFT SWIPE'
        data.expected = 'blue LED ON'
        data.save()
        blue_led.write(1)
    elif action == RIGHT_SWIPE:
        
        data.action = 'RIGHT SWIPE'
        data.expected = 'green LED ON'
        data.save()
        green_led.write(1)
    elif action == DOUBLE_TAP:
        data.action = 'DOUBLE TAP'
        data.expected = 'buzzer beeps twice'
        data.save()
        buzzer.write(1)
        time.sleep(0.3)
        buzzer.write(0)
        time.sleep(0.3)
        buzzer.write(1)
        time.sleep(0.3)
        buzzer.write(0)
    elif action == WAVE:
        data.action = 'WAVE'
        data.expected = 'red LED ON'
        data.save()
        red_led.write(1)
    else:
        data.action = 'UNKNOWN GESTURE'
        data.save()        

# Create your views here
def index(request):    
    all_data = GCAS.objects.order_by('-id')
    table = GCASTable(all_data)
    RequestConfig(request).configure(table)
    context = {'table': table}
    
    return render(request, 'GCAS/index.html', context)

# MAIN
# Inits
tempSensor = mraa.Aio(1)
red_led = mraa.Gpio(2)
green_led = mraa.Gpio(3)
blue_led = mraa.Gpio(4)
buzzer = mraa.Gpio(6)
red_led.dir(mraa.DIR_OUT)
green_led.dir(mraa.DIR_OUT)
blue_led.dir(mraa.DIR_OUT)
buzzer.dir(mraa.DIR_OUT)

mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
if(mqtt_client.connect(broker_address) == 0):
    mqtt_client.loop_start()


