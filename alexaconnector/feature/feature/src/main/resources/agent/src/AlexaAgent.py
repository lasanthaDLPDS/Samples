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

import logging.handlers
import sys,signal, argparse

import threading,calendar

import logging
import time
import running_mode

import fauxmo
from debounce_handler import debounce_handler

import ssl
from functools import wraps

# alexaCalls = {'light on': 0, 'light off': 0, 'buzzer on': 0, 'buzzer off': 0}

iotUtils = __import__('iotUtils')
mqttConnector = __import__('mqttConnector')

PUSH_INTERVAL = 5000  # time interval between successive data pushes in seconds

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#       Logger defaults
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
LOG_FILENAME = "RaspberryStats.log"
logging_enabled = False
LOG_LEVEL = logging.INFO  # Could be e.g. "DEBUG" or "WARNING"
### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#       Python version
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
if sys.version_info < (2, 7, 0):
    sys.stderr.write("You need python 2.7.0 or later to run this script\n")
    exit(1)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#       Define and parse command line arguments
#       If the log file is specified on the command line then override the default
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
parser = argparse.ArgumentParser(description="Python service to push RPi info to the Device Cloud")
parser.add_argument("-l", "--log", help="file to write log to (default '" + LOG_FILENAME + "')")

help_string_for_data_push_interval = "time interval between successive data pushes (default '" + str(PUSH_INTERVAL) + "')"
help_string_for_running_mode = "where is going to run on the real device or not"
parser.add_argument("-i", "--interval", type=int, help=help_string_for_data_push_interval)
parser.add_argument("-m", "--mode", type=str, help=help_string_for_running_mode)

args = parser.parse_args()
if args.log:
    LOG_FILENAME = args.log

if args.interval:
    PUSH_INTERVAL = args.interval


# if args.mode:
#     running_mode.RUNNING_MODE = args.mode
#     iotUtils = __import__('iotUtils')
#     mqttConnector = __import__('mqttConnector')
#     # httpServer = __import__('httpServer') # python script used to start a http-server to listen for operations
#     # (includes the TEMPERATURE global variable)
#
#     if running_mode.RUNNING_MODE == 'N':
#         Adafruit_DHT = __import__('Adafruit_DHT')  # Adafruit library required for temperature sensing


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#       A class we can use to capture stdout and sterr in the log
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class IOTLogger(object):
    def __init__(self, logger, level):
        """Needs a logger and a logger level."""
        self.logger = logger
        self.level = level

    def write(self, message):
        if message.rstrip() != "":  # Only log if there is a message (not just a new line)
            self.logger.log(self.level, message.rstrip())


### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#       Configure logging to log to a file,
#               making a new file at midnight and keeping the last 3 day's data
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def configureLogger(loggerName):
    logger = logging.getLogger(loggerName)
    logger.setLevel(LOG_LEVEL)  # Set the log level to LOG_LEVEL
    handler = logging.handlers.TimedRotatingFileHandler(LOG_FILENAME, when="midnight",
                                                        backupCount=3)  # Handler that writes to a file,
    # ~~~make new file at midnight and keep 3 backups
    formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')  # Format each log message like this
    handler.setFormatter(formatter)  # Attach the formatter to the handler
    logger.addHandler(handler)  # Attach the handler to the logger

    if (logging_enabled):
        sys.stdout = IOTLogger(logger, logging.INFO)  # Replace stdout with logging to file at INFO level
        sys.stderr = IOTLogger(logger, logging.ERROR)  # Replace stderr with logging to file at ERROR level


### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#       This method connects to the Device-Cloud and pushes data
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def connectAndPushData(command, state):
    currentTime = calendar.timegm(time.gmtime())
    PUSH_DATA = iotUtils.DEVICE_INFO.format(currentTime, command, state)

    print '~~~~~~~~~~~~~~~~~~~~~~~~ Publishing Device-Data ~~~~~~~~~~~~~~~~~~~~~~~~~'
    print ('PUBLISHED DATA: ' + PUSH_DATA)
    print ('PUBLISHED TOPIC: ' + mqttConnector.TOPIC_TO_PUBLISH)
    mqttConnector.publish(mqttConnector.TOPIC_TO_PUBLISH, PUSH_DATA)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#       This is a Thread object for reading temperature continuously
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# class CommandReaderThread(object):
#     def __init__(self):
#         if running_mode.RUNNING_MODE == 'N':
#             self.interval = iotUtils.COMMANDS_READING_INTERVAL_REAL_MODE
#         else:
#             self.interval = iotUtils.COMMANDS_READING_INTERVAL_VIRTUAL_MODE
#         thread = threading.Thread(target=self.run, args=())
#         thread.daemon = True  # Daemonize thread
#         thread.start()  # Start the execution
#
#     def run(self):
#
#         # Try to grab a sensor reading.  Use the read_retry method which will retry up
#         # to 15 times to get a sensor reading (waiting 2 seconds between each retry).
#         while True:
#             try:
#                 if running_mode.RUNNING_MODE == 'N':
#
#                 else:
#                     light_on, light_off, buzzer_on, buzzer_off  = iotUtils.generateRandomTemperatureAndHumidityValues(4)
#
#                 # this part shoild be correct
#                 if light_on != iotUtils.LAST_TEMP:
#                     time.sleep(PUSH_INTERVAL)
#                     iotUtils.LAST_TEMP = light_on
#                     connectAndPushData()
#
#                 iotUtils.LAST_TEMP = light_on
#                 # print 'RASPBERRY_STATS: Temp={0:0.1f}*C  Humidity={1:0.1f}%'.format(temperature, humidity)
#
#             except Exception, e:
#                 print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
#                 print "RASPBERRY_STATS: Exception in TempReaderThread: Could not successfully read Temperature"
#                 print ("RASPBERRY_STATS: " + str(e))
#                 pass
#                 time.sleep(self.interval)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#       This is a Thread object for listening for MQTT Messages
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class UtilsThread(object):
    def __init__(self):
        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True  # Daemonize thread
        thread.start()  # Start the execution

    def run(self):
        iotUtils.main()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#       This is a Thread object for connecting and subscribing to an MQTT Queue
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class SubscribeToMQTTQueue(object):
    def __init__(self):
        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True  # Daemonize thread
        thread.start()  # Start the execution

    def run(self):
        mqttConnector.main()


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#       When sysvinit sends the TERM signal, cleanup before exiting
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def sigterm_handler(_signo, _stack_frame):
    print("[] received signal {}, exiting...".format(_signo))
    sys.exit(0)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

signal.signal(signal.SIGTERM, sigterm_handler)

logging.basicConfig(level=logging.DEBUG)


class device_handler(debounce_handler):
    """Publishes the on/off state requested,
       and the IP address of the Echo making the request.
    """
    TRIGGERS = [{"light": 52000}, {"buzzer": 52001}]

    def act(self, client_address, state, name):
        devices = ["BULB", "BUZZER"]
        commands = ["ON", "OFF"]
        msg = None
        try:

            if state == True and name == "light":
                msg = devices[0]+":"+commands[0]

            elif state == True and name == "buzzer":
                msg = devices[1] + ":" + commands[0]

            elif state == False and name == "light":
                msg = devices[0] + ":" + commands[1]

            elif state == False and name == "buzzer":
                msg = devices[1] + ":" + commands[1]

            if msg == None:
                logging.error("Invalid message")
            else:

                mqttConnector.publish(mqttConnector.TOPIC_TO_PUBLISH_BRAIN_WAVE_INFO, msg)
                connectAndPushData(msg.split(":")[0], msg.split(":")[1])
                msg = None

            return True
        except Exception, e:
            logging.critical("Critical exception: " + str(e))


def test(state, name):
    devices = ["BULB", "BUZZER"]
    commands = ["ON", "OFF"]
    msg = None
    try:

        if state == True and name == "light":
            msg = devices[0] + ":" + commands[0]

        elif state == True and name == "buzzer":
            msg = devices[1] + ":" + commands[0]

        elif state == False and name == "light":
            msg = devices[0] + ":" + commands[1]

        elif state == False and name == "buzzer":
            msg = devices[1] + ":" + commands[1]

        if msg == None:
            logging.error("Invalid message")
        else:

            mqttConnector.publish(mqttConnector.TOPIC_TO_PUBLISH_BRAIN_WAVE_INFO, msg)
            connectAndPushData(msg.split(":")[0], msg.split(":")[1])
            msg = None

        return True
    except Exception, e:
        logging.critical("Critical exception: " + str(e))

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#       The Main method of the RPi Agent
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def main():

    configureLogger("WSO2IOT_RPiStats")
    UtilsThread()
    SubscribeToMQTTQueue()  # connects and subscribes to an MQTT Queue that receives MQTT commands from the server
    # CommandReaderThread()

    # Startup the fauxmo server
    fauxmo.DEBUG = True
    p = fauxmo.poller()
    u = fauxmo.upnp_broadcast_responder()
    u.init_socket()
    p.add(u)

    # Register the device callback as a fauxmo handler
    d = device_handler()

    for x in d.TRIGGERS:
        trig, port = x.items()[0]
        fauxmo.fauxmo(trig, u, p, None, port, d)

    # Loop and poll for incoming Echo requests
    logging.debug("Entering fauxmo polling loop")
    while True:

        test(True,"light")
        time.sleep(0.8)
        test(False, "light")
        time.sleep(0.9)
        test(True, "buzzer")
        time.sleep(0.8)

        test(False, "buzzer")
        time.sleep(0.8)
    # while True:
    #     try:
    #         # Allow time for a ctrl-c to stop the process
    #         p.poll(100)
    #         time.sleep(0.1)
    #     except Exception, e:
    #         logging.critical("Critical exception: " + str(e))
    #         break

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__ == "__main__":
    main()
