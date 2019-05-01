# GCAS
This is a repo for the GCAS EECS6765 Advanced IoT Spring 2019 Final Project.

This repo is split among multiple folders to indicate where different scripts are found.

In this project, the goal is to take sensor data from the GCAS wearable and train a machine learning model on AWS to ultimately obtain predictions for gesture recognition. To expand further, the predictions obtained are sent to other devices through the MQTT protocol. All the predictions and expected outcomes are also posted onto a webpage.


**RaspberryPi**
1. Hosts MQTT server through mosquitto installation and automatic server setup upon startup
2. Collects, formats, and preprocesses individual sensor readings
3. In training mode, the RaspberryPi will send a .csv file to an S3 bucket where AWS Sagemaker can access
4. In prediction mode, the RaspberryPi will send the cleaned sensor readings to an AWS Sagemaker endpoint and receive a prediction label 
5. In prediction mode, the prediction label is then pushed to an MQTT topic.

**IntelEdison**
1. Hosts Django web page
2. Connects as MQTT subscriber to the same topic as RaspberryPi publisher
3. Upon a new published message from the RaspberryPi, the IntelEdison will perform different actions.
4. No matter which action is performed, the web page is also updated with the prediction gesture, the raw label, and the expected action upon an MQTT message reception

**AWS SageMaker**
1. Needs to be used as an AWS SageMaker instanced (or have already installed AWS SageMaker SDK for Python) as per their tutorial. Most of the code is derived from the tutorials.
2. Accesses S3 bucket containing training data, performs training job for XGBoost multiclassification, creates endpoint which contains the model artifacts capable for real-time predictions.
3. The Jupyter notebook needs to be rerun every time a new model is needed. It will update the existing 'GCAS' endpoint.
*NOTE: creating/updating an endpoint takes a long time (~ 5-10 minutes)*

**Terminal**
1. Connects as MQTT subscriber to the same topic as RaspberryPi publisher
2. Upon a new published message from RaspberryPi, the Terminal will perform different actions.
3. No matter which action is performed, the Terminal will always print out the prediction gesture
