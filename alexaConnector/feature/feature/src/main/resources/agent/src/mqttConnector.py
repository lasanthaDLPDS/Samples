#!/usr/bin/env python

"""
/**
* Copyright (c) 2017, WSO2 Inc. (http://www.wso2.org) All Rights Reserved.
*
* WSO2 Inc. licenses this file to you under the Apache License,
* Version 2.0 (the "License"); you may not use this file except
* in compliance with the License.
* You may obtain a copy of the License at
*
* http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing,
* software distributed under the License is distributed on an
* "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
* KIND, either express or implied. See the License for the
* specific language governing permissions and limitations
* under the License.
**/
"""

import time

import iotUtils
import paho.mqtt.client as mqtt


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    if(rc == 4):
        print "Device Unable to connect Broker"
    elif rc == 0:
        print "Device connected with Broker"
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    #print ("MQTT_LISTENER: Subscribing with topic " + TOPIC_TO_SUBSCRIBE)
    # client.subscribe(TOPIC_TO_SUBSCRIBE)


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
    print 'MQTT_LISTENER: Message Received by Device'
    print("MQTT_LISTENER: " + msg.topic + " --> " + str(msg.payload))

    request = str(msg.payload)

    resource = request.split(":")[0].upper()
    state = request.split(":")[1].upper()

    print "MQTT_LISTENER: Resource- " + resource


def on_publish(client, userdata, mid):
    print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
    print 'Alexa Connector Data Published Succesfully'
    # print (client)
    # print (userdata)
    # print (mid)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#       The callback for when a PUBLISH message to the server when door is open or close
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def publish(msg):
    #   global mqttClient

    print "Publish triggered...."
    mqttClient.publish(TOPIC_TO_PUBLISH_BRAIN_WAVE_INFO, msg)
    print "published to topic " + str(msg) + str(TOPIC_TO_PUBLISH_BRAIN_WAVE_INFO)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#       The Main method of the server script
#           This method is invoked from RaspberryStats.py on a new thread
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def main():
    MQTT_ENDPOINT = iotUtils.MQTT_EP.split(":")
    MQTT_IP = MQTT_ENDPOINT[1].replace('//', '')
    MQTT_PORT = int(MQTT_ENDPOINT[2])

    SERVER_NAME = iotUtils.SERVER_NAME
    DEV_ID = iotUtils.DEVICE_ID

    global TOPIC_TO_SUBSCRIBE
    TOPIC_TO_SUBSCRIBE = SERVER_NAME + "/raspberrypi/alexa"

    global TOPIC_TO_PUBLISH_BRAIN_WAVE_INFO
    TOPIC_TO_PUBLISH_BRAIN_WAVE_INFO = SERVER_NAME + "/alexa/raspberrypi"

    print ("MQTT_LISTENER: MQTT_ENDPOINT is " + str(MQTT_ENDPOINT))
    print ("MQTT_LISTENER: MQTT_TOPIC is " + TOPIC_TO_SUBSCRIBE)

    global mqttClient
    mqttClient = mqtt.Client()
    mqttClient.on_connect = on_connect
    mqttClient.on_message = on_message
    mqttClient.on_publish = on_publish
    mqttClient.username_pw_set(iotUtils.AUTH_TOKEN, password="")
    # mqttClient.username_pw_set("admin", password="admin")

    while True:
        try:
            mqttClient.connect(MQTT_IP, MQTT_PORT, 180)
            print "MQTT_LISTENER: " + time.asctime(), "Connected to MQTT Broker - %s:%s" % (MQTT_IP, MQTT_PORT)

            # Blocking call that processes network traffic, dispatches callbacks and
            # handles reconnecting.
            # Other loop*() functions are available that give a threaded interface and a
            # manual interface.
            mqttClient.loop_forever()

        except (KeyboardInterrupt, Exception) as e:
            print "MQTT_LISTENER: Exception in MQTTServerThread (either KeyboardInterrupt or Other)"
            print ("MQTT_LISTENER: " + str(e))

            mqttClient.disconnect()
            print "MQTT_LISTENER: " + time.asctime(), "Connection to Broker closed - %s:%s" % (MQTT_IP, MQTT_PORT)
            print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
            pass


if __name__ == '__main__':
    main()