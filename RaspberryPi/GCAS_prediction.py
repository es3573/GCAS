#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May  1 16:58:36 2019

@author: eriksu
"""

import board
import busio
import adafruit_bno055
import adafruit_lis3dh
import adafruit_tca9548a
import RPi.GPIO as GPIO

import time
import numpy as np
import csv
import aws
import paho.mqtt.client as mqtt

# Definitions
TRAIN = 1
PREDICT = 2
EXIT = 3
button_pin = 18
NUM_FEATURES =  37*10+1# 221 = 1 (label) + 10 readings * (22(bno)+15(3*5axls) features/reading)
training_data = 'training_data.csv'
bucket = 'sagemaker-gcas'
prefix = 'sagemaker/xgboost'
endpoint_name = 'GCAS2019-05-01-18-35-20'
broker_address = '192.168.0.24'
uplink_topic = "topic/gcas/prediction"

# Local Functions
# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    client.subscribe(uplink_topic)
    print('Subscribed to ' + uplink_topic)
    
# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    #print('\n\rMQTT message: ' + str(msg.payload))
    pass
        
# Retrieve raw data from sensors and format them
def get_reading(label):
    final_readings = [label]
    started_reading = 0
    first_reading = 0
    print('\n\rHold button while performing training gesture')
    while (started_reading == 0):
        button_pressed = GPIO.input(button_pin)
        while((button_pressed == 0) and (len(final_readings) != NUM_FEATURES)):
            started_reading = 1
            if (first_reading == 0):
                buffer = []
                sensor_readings = get_raw_data(buffer)
                sensor_buffer = sensor_readings
                sensor_stacked = []
                sensor_stacked.append(sensor_buffer)
                first_reading = 1
            else:
                buffer = []
                sensor_readings = get_raw_data(buffer)
                sensor_buffer = sensor_readings
                sensor_stacked.append(sensor_buffer)
                sensor_readings = [np.subtract(sensor_stacked[x-1],sensor_stacked[x]) for x in range(0,1)]
                sensor_readings = sensor_readings[0].tolist()
                [final_readings.append(x) for x in sensor_readings]
                
            button_pressed = GPIO.input(button_pin)
            
        if (len(final_readings) == NUM_FEATURES):
            started_reading = 0
            first_reading = 1
            return final_readings 
        
        elif ((button_pressed == 1) and (started_reading == 1)):
            started_reading = 0
            first_reading = 1
            print('\n\rError reading sensors! Try again.\n\r')
            break
    return final_readings

def get_raw_data(sensor_readings):
    [sensor_readings.append(i) for i in bno_sensor.acceleration]
    [sensor_readings.append(i) for i in bno_sensor.magnetic]
    [sensor_readings.append(i) for i in bno_sensor.gyroscope]
    [sensor_readings.append(i) for i in bno_sensor.euler]
    [sensor_readings.append(i) for i in bno_sensor.quaternion]
    [sensor_readings.append(i) for i in bno_sensor.linear_acceleration]
    [sensor_readings.append(i) for i in bno_sensor.gravity]
    for i in range(0,5):
        list_buffer = [value / adafruit_lis3dh.STANDARD_GRAVITY for value in axl_array[i].acceleration]
        [sensor_readings.append(i) for i in list_buffer]
    return sensor_readings
    
# Process training data
def send_training():
    label = input("\n\rEnter Label number or -1 to update:   ")
    
    while int(label) != -1:
        sensor_readings = get_reading(label)
        if (len(sensor_readings) == NUM_FEATURES):
            print('Data collected.')
            with open(training_data, 'a') as f:
                writer = csv.writer(f)
                writer.writerow(sensor_readings)
                print("Saved.")
        label = input("Enter Label number or '-1' to update:   ")
    # upload to S3 bucket for SageMaker instance (will overwrite)
    print("Updating S3")    
    s3_client.upload_file(training_data, bucket, prefix + "/train.csv")
    
        
# Retrieve prediction data
def request_prediction():
    sensor_readings = get_reading(-1)
    if (len(sensor_readings) == NUM_FEATURES):
        print('Data collected.')
        sensor_readings.pop(0)
        sensor_readings = [str(x) for x in sensor_readings]
        sensor_readings = ','.join(sensor_readings)
        
        print("Invoking AWS SageMaker endpoint")
        response = runtime_client.invoke_endpoint(EndpointName=endpoint_name, 
                                                  ContentType='text/csv',
                                                  Body=sensor_readings)
        result = response['Body'].read().decode('ascii')
        print('Predicted label is {}.'.format(result))
        print('Publishing to ' + uplink_topic)
        mqtt_client.publish(uplink_topic, int(float(result)))   
    else:
        print('Something went wrong. Try again')

# MAIN
# I2C inits
print("\n\rInitializing hardware and clients . . .")
i2c = busio.I2C(board.SCL, board.SDA)

mux = adafruit_tca9548a.TCA9548A(i2c)
bno_sensor = adafruit_bno055.BNO055(mux[0])
axl_array = []
for i in range(1,6):
    axl_array.append(adafruit_lis3dh.LIS3DH_I2C(mux[i]))

GPIO.setmode(GPIO.BCM)
GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
button_pressed = GPIO.input(button_pin)

# Clients    
s3_client = aws.getClient('s3','us-east-1')
runtime_client = aws.getClient('runtime.sagemaker', 'us-east-1')
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

# Main Loop
print("Connecting to MQTT Broker . . .")
if(mqtt_client.connect(broker_address) == 0):
    mqtt_client.loop_start()
    print('PREDICTION ONLY MODE')
    while True:
        request_prediction()
        time.sleep(5)
        pass
