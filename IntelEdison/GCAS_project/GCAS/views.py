# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django_tables2 import RequestConfig

from .models import GCAS
from .tables import GCASTable

import paho.mqtt.client as mqtt
import mraa
import math

# Defines
NO_MOTION = 0
LEFT_SWIPE = 1
RIGHT_SWIPE = 2
UP_SWIPE = 3
DOWN_SWIPE = 4

broker_address = '192.168.0.24'
downlink_topic = "topic/gcas/prediction"
uplink_topic = "topic/gcas/uplink"

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

# process prediction for action
def process_prediction(payload, data):
    action = int(payload)
    if action == NO_MOTION:
        current_temp = convert_temp(tempSensor.read())
        data.temperature = current_temp
        data.action = 'NO MOTION'
        data.expected = 'keyboard write'
        data.save()
    elif action == LEFT_SWIPE:
        data.action = 'LEFT SWIPE'
        data.save()
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
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
if(mqtt_client.connect(broker_address) == 0):
    mqtt_client.loop_start()


