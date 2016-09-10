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
from Sensors import Sensors, Sensor_DHT
from AwsPubSub import AwsClient
from Configuration import Configuration

##----- testing -----------------------------------------------------------------
debugthis = False
    

            
##----- globals -----------------------------------------------------------------
cfg = None
state = None
thismodule = None


##----- configuration -----------------------------------------------------------------
new_configuration = {
    'name' : 'DHT_THING',               # name of thing
    'publish' : 'unassigned',           # topic to publish on
    'subscribe' : 'unassigned_reply',   # topic to reply on
    'interval' : '3600',                # default interval = 1 hour = 60*60 secs
    'qos' : '0',                        # quality of service needed for this thing
    'hwpin' : '0',
    'hwtype' : ''
    }
    
    
##----- defs -----------------------------------------------------------------
def subscribe_callback(client, userdata, message):
    global cfg, state
    # MQTT message callback
    try:
        control = ast.literal_eval(message.payload.decode())
        if debugthis: print ("control ", control)

        if 'state' in control and control['state'] == '?':
            if debugthis: print ("state ", state)
            client.publish(
                    cfg.configuration['publish'],
                    json.dumps({'ack':'state '+state}),
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
                                        
        elif 'hwpin' in control and int(control['hwpin']) > 0:
            cfg.configuration['hwpin'] = control['hwpin']
            state = 'ready'
            if debugthis: print ("new hwpin ", cfg.configuration['hwpin'])
            client.publish(
                    cfg.configuration['publish'],
                    json.dumps({'ack':'hwpin '+cfg.configuration['hwpin']}),
                    1
                    )
                                        
        elif 'hwtype' in control and control['hwtype'] is not "":
            cfg.configuration['hwtype'] = control['hwtype']
            state = 'ready'
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
            state = 'connect'

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


##----- main -----------------------------------------------------------------

def __main__(argv):
    global cfg, state, thismodule
    args = None
    state = 'init'
    thismodule = os.path.splitext(os.path.basename(sys.argv[0]))[0]

    if debugthis and len(sys.argv) == 1:
        import args_gitignore
        for arg1 in args_gitignore.test_args:git 
            sys.argv.extend(arg1)
        print (sys.argv)
        with open('call.txt', 'w') as fileout:
            fileout.write(str(sys.argv))

        
    while state is not 'stop':

        if state is 'init':
            try:
                args = process_command_line_parameters()
                cfile = os.path.dirname(os.path.realpath(__file__)) \
                             +  '/' + thismodule + '.conf'
                if debugthis:
                    print ("configfile ", cfile)
                           
                cfg = Configuration(cfile, new_configuration)
                if cfg.read() is not None:
                    state = 'connect'
            except:
                raise

        if state is 'connect':
            try:
                # get instance of AWS IOT services
                mymqtt = AwsClient(
                    thismodule,
                    args.endpoint,
                    int(args.port),
                    args.rootCA,
                    args.cert,
                    args.key
                    )
                # connect to AWS
                connect_attempts = 3
                while mymqtt.connect() == False and connect_attempts > 0:
                    time.sleep(5)
                    connect_attempts -= 1
                if connect_attempts > 0:
                    state = 'subscribe'
            except:
                raise

        if state is 'subscribe':
            try:
                # subscribe to control topic, QoS must be 1 to ensure responsiveness
                connect_attempts = 3
                if debugthis:
                    print("state subscribe")
                    print("subscribe ", cfg.configuration['subscribe'])
                    
                while (mymqtt.subscribe(
                        cfg.configuration['subscribe'],
                        1,
                        subscribe_callback
                        )
                       == False and connect_attempts > 0):
                    time.sleep(5)
                    connect_attempts -= 1
                if connect_attempts > 0:
                    state = 'ready'
            except:
                raise
    
        if state is 'ready':
            try:
                if debugthis:
                    print ("hwpin ", cfg.configuration['hwpin'])
                    print ("hwtype ", cfg.configuration['hwtype'], Sensor_DHT.DHT[cfg.configuration['hwtype']])
                with Sensor_DHT(
                        pin=cfg.configuration['hwpin'],
                        type=Sensor_DHT.DHT[cfg.configuration['hwtype']]
                        ) as myDHT:
                    if myDHT is not None:
                        state = 'active'
                    while state is 'active':
                        try:
                            # get DHT readings and timestamp
                            readtime, humidity, temperature = myDHT.read()
                            dht = {
                                'timestamp' : readtime,
                                'humidity' : humidity,
                                'temperature' : temperature
                                }
                            # publish the data
                            json_data = json.dumps(dht)
                            mymqtt.publish(
                                cfg.configuration['publish'],
                                json_data,
                                int(cfg.configuration['qos'])
                                )

                            # wait for the next interval
                            now = time.time()
                            while time.time() < now + int(cfg.configuration['interval']):
                                time.sleep(1)
                        except:
                            raise   
            except:
                raise

##        if state is 'disconnect':
##            try:
##                mymqtt.unsubscribe(cfg.configuration['subscribe'])
##                mymqtt.disconnect()
##                state = 'connect'
##            except:
##                return True
    
if __name__ == "__main__":
    __main__(sys.argv[1:])
