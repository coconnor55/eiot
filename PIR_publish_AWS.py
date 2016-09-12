#!/usr/bin/python3
""" DHT_publish_AWS 
##Copyright 2016 Clint H. O'Connor
##
##   Licensed under the Apache License, Version 2.0 (the "License");
##   you may not use this file except in compliance with the License.
##   You may obtain a copy of the License at
##
##       http://www.apache.org/licenses/LICENSE-2.0
##
##   Unless required by applicable law or agreed to in writing, software
##   distributed under the License is distributed on an "AS IS" BASIS,
##   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
##   See the License for the specific language governing permissions and
##   limitations under the License.
"""

##----- imports -----------------------------------------------------------------
import os
import sys
import ast
import time
import json
import argparse
from Sensors import Sensors, Sensor_PIR, SensorState
from AwsPubSub import AwsClient
from Configuration import Configuration

##----- testing -----------------------------------------------------------------
debugthis = True
    

            
##----- globals -----------------------------------------------------------------
args = None
cfg = None
run_state = None
alert_state = None
thismodule = None
mymqtt = None


##----- configuration -----------------------------------------------------------------
new_configuration = {
    'name' : 'PIR_THING',               # name of thing
    'publish' : 'unassigned',           # topic to publish on
    'subscribe' : 'unassigned_reply',   # topic to reply on
    'interval' : '3600',                # default interval = 1 hour = 60*60 secs
    'qos' : '1',                        # quality of service needed for this thing
    'hwpin' : '0',
    'hwtype' : ''
    }
    
    
##----- defs -----------------------------------------------------------------
def subscribe_callback(client, userdata, message):
    global cfg, run_state
    # MQTT message callback
    try:
        control = ast.literal_eval(message.payload.decode())
        if debugthis: print ("control ", control)

        if 'state' in control and control['state'] == '?':
            if debugthis: print ("state ", run_state)
            client.publish(
                    cfg.configuration['publish'],
                    json.dumps({'ack':'state '+run_state}),
                    1
                    )

        elif 'configuration' in control:
            if control['configuration'] == '?':
                if debugthis: print ("configuration ", cfg.configuration)
                client.publish(
                        cfg.configuration['publish'],
                        json.dumps(cfg.configuration),
                        1
                        )
            elif control['configuration'] == 'save':
                if debugthis: print ("saved configuration file")
                cfg.write()
                client.publish(
                        cfg.configuration['publish'],
                        json.dumps({'ack':'saved configuration file'}),
                        1
                        )

        elif 'interval' in control and int(control['interval']) >= 1:
            cfg.configuration['interval'] = control['interval']
            if debugthis: print ("new interval ", cfg.configuration['interval'])
            client.publish(
                    cfg.configuration['publish'],
                    json.dumps({'ack':'interval '+cfg.configuration['interval']}),
                    1
                    )
                                        
        elif 'qos' in control and int(control['qos']) >= 1:
            cfg.configuration['qos'] = control['qos']
            if debugthis: print ("new qos ", cfg.configuration['qos'])
            client.publish(
                    cfg.configuration['publish'],
                    json.dumps({'ack':'qos '+cfg.configuration['qos']}),
                    1
                    )
                                        
        elif 'hwpin' in control and int(control['hwpin']) > 0:
            cfg.configuration['hwpin'] = control['hwpin']
            run_state = 'ready'
            if debugthis: print ("new hwpin ", cfg.configuration['hwpin'])
            client.publish(
                    cfg.configuration['publish'],
                    json.dumps({'ack':'hwpin '+cfg.configuration['hwpin']}),
                    1
                    )
                                        
        elif 'hwtype' in control and control['hwtype'] is not "":
            cfg.configuration['hwtype'] = control['hwtype']
            run_state = 'ready'
            if debugthis: print ("new hwtype ", cfg.configuration['hwtype'])
            client.publish(
                    cfg.configuration['publish'],
                    json.dumps({'ack':'hwtype '+cfg.configuration['hwpin']}),
                    1
                    )
                                        
        elif 'publish' in control:
            # unsubscribe and disconnect immediately
            client.publish(
                    cfg.configuration['publish'],
                    json.dumps({'ack':'changing topic to '+control['publish']}),
                    1
                    )
            client.unsubscribe(cfg.configuration['subscribe'])
            client.disconnect()

            # set up new mqtt channels
            cfg.configuration['publish'] = control['publish']
            cfg.configuration['subscribe'] = control['publish'] + '_reply'
            if debugthis:
                print ("new publish ", cfg.configuration['publish'])
                print ("new subscribe ", cfg.configuration['subscribe'])
            run_state = 'connect'

        elif 'Reb00t' in control and control['Reb00t'] == 'True':
            client.publish(
                    cfg.configuration['publish'],
                    json.dumps({'ack':'rebooting...'}),
                    1
                    )
            command = "/usr/bin/sudo /sbin/shutdown -r now"
            import subprocess
            process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
            output = process.communicate()[0]

    except:
        if debugthis:
            print("Unprocessed message: ")
            print(message.payload)
            print("from topic: ")
            print(message.topic)
            print("--------------\n\n")
        pass


def PIR_motion_callback(self, pin, width):
    global mymqtt
    
    if debugthis: print ("PIR event on pin ", pin, width)
    readtime = time.gmtime()
    pir = {
        'timestamp' : readtime,
        'event' : 'motion',
        'duration' : str(width)
        }
    mymqtt.publish(
            cfg.configuration['publish'],
            json.dumps(pir),
            1
            )
    return
        
def PIR_rising_callback(self, pin):
    global mymqtt, run_state
    
    if debugthis: print ("PIR rising event on pin ", pin)
    readtime = time.gmtime()
    pir = {
        'timestamp' : readtime,
        'event' : 'rising edge',
        }
    mymqtt.publish(
            cfg.configuration['publish'],
            json.dumps(pir),
            1
            )
    return

def sensor_callback(self, state):
    global mymqtt, run_state
    
    if debugthis: print ("sensor callback - entering state ", state)
    #if state is 'sleep':  return
    
    readtime = time.gmtime()
    pir = {
        'timestamp' : readtime,
        'state' : state,
        }
    mymqtt.publish(
            cfg.configuration['publish'],
            json.dumps(pir),
            1
            )

def process_command_line_parameters():
    """ process command line parameters
    -e endpoint
    -r root CA
    -c cert
    -k private key
    -p port
    """
    global thismodule
    
    # process command line parameters
    parser = argparse.ArgumentParser("Description: " + thismodule)
    parser.add_argument('-e','--endpoint', help='Root CA file path',required=True)
    parser.add_argument('-r','--rootCA', help='Root CA file path',required=True)
    parser.add_argument('-c','--cert', help='Certificate file path',required=True)
    parser.add_argument('-k','--key', help='Private key file path',required=True)
    parser.add_argument('-p','--port', help='Port number',required=True)
    args = parser.parse_args()

    if debugthis:
        print("endpoint ", args.endpoint)
        print("rootCA ", args.rootCA)
        print("cert ", args.cert)
        print("key ", args.key)
        print("port ", args.port)
    return args

def init():
    global args, cfg
    args = process_command_line_parameters()
    cfile = os.path.dirname(os.path.realpath(__file__))+'/'+thismodule+'.conf'
    if debugthis: print ("configfile ", cfile)
               
    cfg = Configuration(cfile, new_configuration)
    return (cfg.read() is not None)
    
def connect(args):
    # get instance of AWS IOT services
    mqtt = AwsClient(
        thismodule,
        args.endpoint,
        int(args.port),
        args.rootCA,
        args.cert,
        args.key
        )
    # connect to AWS
    connect_attempts = 3
    while mqtt.connect() == False and connect_attempts > 0:
        time.sleep(3)
        connect_attempts -= 1
    return mqtt, connect_attempts > 0

def subscribe(mqtt, topic, callback):
    # subscribe to control topic, QoS must be 1 to ensure responsiveness
    connect_attempts = 3
    while (mqtt.subscribe(topic, 1, callback) == False and connect_attempts > 0):
        time.sleep(3)
        connect_attempts -= 1
    return (connect_attempts > 0)

def next_sensor_state(alert_state, sensor_state, sensor_count):
    if alert_state is 'ready':
        if sensor_state == 0:
            alert_time = int(time.time()*1000)
            return 'ready'
        else:
            return 'awake'
    elif alert_state is 'awake':
            elapsed_time = int(time.time()*1000) - alert_time
    
    

##----- main -----------------------------------------------------------------

def __main__(argv):
    global args, cfg, run_state, thismodule, mymqtt

    run_state = 'init'
    thismodule = os.path.splitext(os.path.basename(sys.argv[0]))[0]

    if debugthis and len(sys.argv) == 1:
        import args_gitignore
        for arg1 in args_gitignore.test_args:
            sys.argv.extend(arg1)
        print (sys.argv)
        with open('call.txt', 'w') as fileout:
            fileout.write(str(sys.argv))

        
    while run_state is not 'stop':

        if run_state is 'init':
            if init() is True: 
                run_state = 'connect'

        if run_state is 'connect':
            mymqtt, result = connect(args)
            if result is True:
                run_state = 'subscribe'

        if run_state is 'subscribe':
            if subscribe(mymqtt, cfg.configuration['subscribe'], subscribe_callback):
                run_state = 'ready'
                
        if run_state is 'ready':
            with Sensor_PIR(
                    pin=cfg.configuration['hwpin'],
                    type=Sensor_PIR.PIR[cfg.configuration['hwtype']]
                    ) as myPIR:

                if myPIR is not None:
                    myPIRState = SensorState(myPIR, callback=sensor_callback)
                    #myPIR.register_callback(rising=PIR_rising_callback, motion=PIR_motion_callback)
                    run_state = 'active'

                now = time.time()
                while run_state is 'active':
                    try:                        
                        myPIRState.evaluate()
                        
                        if time.time() > now + int(cfg.configuration['interval']):
                            now = time.time()
                            # get PIR status
                            readtime, pirstate, pirrisingcount, pirfallingcount = myPIR.read()
                            pir = {
                                'timestamp' : readtime,
                                'instant' : pirstate,
                                'risingcount' : pirrisingcount,
                                'fallingcount' : pirfallingcount
                                }
                            # publish the data
                            json_data = json.dumps(pir)
                            mymqtt.publish(
                                cfg.configuration['publish'],
                                json_data,
                                int(cfg.configuration['qos'])
                                )
                            # reset the PIR count
                            #myPIR.reset_count()
                            
                        # wait for the next interval
                        time.sleep(0.5)
                    except:
                        raise

##                    if alert_state is 'alert':
##                        if debugthis: print("state ", run_state)
##                        alert_time = time.gmtime()
##                        myPIR.reset_count()
##                        while state is 'alert':
    
if __name__ == "__main__":
    __main__(sys.argv[1:])
