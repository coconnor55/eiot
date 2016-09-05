''' Module AwsPubSub 
##Copyright 2016 Clint H. O'Connor
   limitations under the License.
/*
 * Copyright 2010-2016 Amazon.com, Inc. or its affiliates. All Rights Reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License").
 * You may not use this file except in compliance with the License.
 * A copy of the License is located at
 *
 *  http://aws.amazon.com/apache2.0
 *
 * or in the "license" file accompanying this file. This file is distributed
 * on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
 * express or implied. See the License for the specific language governing
 * permissions and limitations under the License.
 */
 '''

##----- imports -----------------------------------------------------------------
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient


##----- classes --------------------------------------------------------------------

class AwsClient(object):
    """ MQTT client with pub/sub """

    def __init__(self, clientname, host, port, rootCAPath, certificatePath, privateKeyPath):
        try:
            self.clientname = clientname

            # Init AWSIoTMQTTClient
            self.myAWSIoTMQTTClient = None
            self.myAWSIoTMQTTClient = AWSIoTMQTTClient(self.clientname)
            self.myAWSIoTMQTTClient.configureEndpoint(host, port)
            self.myAWSIoTMQTTClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

            # AWSIoTMQTTClient connection configuration
            self.myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
            self.myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
            self.myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
            self.myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
            self.myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec
        except:
            raise Exception(__doc__ + ".AwsClient.__init__ crashed")

    def __del__(self):
        try:
            return self.myAWSIoTMQTTClient.disconnect()
        except:
            pass

    def connect(self):
        try:
            return self.myAWSIoTMQTTClient.connect()
        except:
            raise Exception(__doc__ + ".AwsClient.connect crashed")

    def disconnect(self):
        try:
            return self.myAWSIoTMQTTClient.disconnect()
        except:
            raise Exception(__doc__ + ".AwsClient.disconnect crashed")

    def publish(self, topic, payload, QoS):
        try:
            if QoS < 0 or QoS > 1:
                return False
            return self.myAWSIoTMQTTClient.publish(topic, payload, QoS)
        except:
            raise Exception(__doc__ + ".AwsClient.publish crashed")

    def subscribe(self, topic, QoS, callback):
        try:
            if QoS < 0 or QoS > 1:
                return False
            return self.myAWSIoTMQTTClient.subscribe(topic, QoS, callback)
        except:
            raise Exception(__doc__ + ".AwsClient.subscribe crashed")

    def unsubscribe(self, topic):
        try:
            return self.myAWSIoTMQTTClient.unsubscribe(topic)
        except:
            raise Exception(__doc__ + ".AwsClient.unsubscribe crashed")
            

    # Custom MQTT message callback
    def customCallback(client, userdata, message):
            print("Received a new message: ")
            print(message.payload)
            print("from topic: ")
            print(message.topic)
            print("--------------\n\n")

