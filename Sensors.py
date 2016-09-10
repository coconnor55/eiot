""" Module Sensors """
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
   

##----- imports -----------------------------------------------------------------
import time
import RPi.GPIO as GPIO
import Adafruit_DHT


##----- classes --------------------------------------------------------------------

class Sensors(object):
    """ Sensors is a base class for different sensor types """

    _opencount = 0

    def __init__(self):
        Sensors._opencount += 1

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass
##        Sensors._opencount -= 1
##        if Sensors._opencount is 0:
##            GPIO.cleanup()

    def __del__(self):
        Sensors._opencount -= 1
        if Sensors._opencount is 0:
            GPIO.cleanup()
##        GPIO.cleanup()
        pass
        
class Sensor_DHT(Sensors):
    """ Sensor_DHT is a digital humidity/temperature class of sensor """
    DHT = {
        'DHT11' : Adafruit_DHT.DHT11,
        'DHT22' : Adafruit_DHT.DHT22
        }

##    def __init__(self, pin, sensortype):
    '''__init__
    pin= GPIO pin of sensor
    type= type of sensor
    '''
    def __init__(self, **args):
        Sensors.__init__(self)
        self.pin = args['pin']
        self.sensortype = args['type']
        self.currenthumidity = 0
        self.currenttemperature = 0

    def __enter__(self):
        Sensors.__enter__(self)
        return self

    def __exit__(self, type, value, traceback):
        Sensors.__exit__(self, type, value, traceback)

    def __del__(self):
        Sensors.__del__(self)

    def read(self):
        try:
            self.currenthumidity, self.currenttemperature = Adafruit_DHT.read_retry(self.sensortype, self.pin)
            if self.currenthumidity is not None and self.currenttemperature is not None:
                return time.gmtime(), self.currenthumidity, self.currenttemperature
            else:
                return time.gmtime(), None, None
        except:
            raise Exception(__doc__.strip() + ".read crashed")            

    
class Sensor_PIR(Sensors):
    """ Sensor_PIR is a passive infrared motion detector class of sensor """
    PIR = {
        'PIR_HC_SR501' : 1
        }

    def __init__(self, **args):
        Sensors.__init__(self)
        try:
            Sensors.__init__(self)
            self.pin = args['pin']
            self.sensortype = args['type']
            self.events = 0
            self.count = 0
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.pin, GPIO.IN)
        except:
            raise Exception(__doc__.strip() + ".__init__ crashed")

    def __enter__(self):
        Sensors.__enter__(self)
        return self

    def __exit__(self, type, value, traceback):
        Sensors.__exit__(self, type, value, traceback)

    def __del__(self):
        Sensors.__del__(self)
    
    def read(self):
        try:
            return time.gmtime(), GPIO.input(self.pin)
        except:
            raise Exception("crashed: Sensor_PIR::read")

    def reset_count(self):
        self.count = 0

    def register_callback(self, callback2=None):
        try:
            GPIO.add_event_detect(self.pin, GPIO.RISING, bouncetime=50)
            GPIO.add_event_callback(self.pin, callback=self.standard_callback)
            if callback2 is not None:
                GPIO.add_event_callback(self.pin, callback=callback2)
            return

        except:
            raise Exception("crashed: Sensor_PIR::register_callback")

    def standard_callback(self, pin):
        self.count = self.count + 1
        return
        

