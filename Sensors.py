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
import atexit
from io import BytesIO
from picamera import PiCamera
from PIL import Image
import RPi.GPIO as GPIO
import Adafruit_DHT


##----- classes --------------------------------------------------------------------

class Sensors(object):
    """ Sensors is a base class for different sensor types """

    opencount = 0
    PIR_HC_SR501 = 1

    def __init__(self):
        try:
            Sensors.opencount += 1
            return
        except:
            raise Exception("crashed: Sensors::__init__")

    def __del__(self):
        try:
            Sensors.opencount -= 1
            if Sensorslf.opencount is 0:
                GPIO.cleanup()
            return
        except:
            raise Exception("crashed: Sensors::__del__")

    def cleanup():
        GPIO.cleanup()
        return

        
class Sensor_DHT(Sensors):
    """ Sensor_DHT is a digital humidity/temperature class of sensor """
    DHT11 = Adafruit_DHT.DHT11
    DHT22 = Adafruit_DHT.DHT22

##    def __init__(self, pin, sensortype):
    def __init__(self, **args):
        try:
            Sensors.__init__(self)
            self.pin = args["pin"]
            self.sensortype = args["type"]
            self.currenthumidity = 0
            self.currenttemperature = 0
            return
        except:
            raise Exception("crashed: Sensor_DHT::__init__")

    def __del__(self):
        try:
            Sensors.__del__(self)
            return
        except:
            raise Exception("crashed: Sensor_DHT::__del__")

    def read(self):
        try:
            self.currenthumidity, self.currenttemperature = Adafruit_DHT.read_retry(self.sensortype, self.pin)
            if self.currenthumidity is not None and self.currenttemperature is not None:
                return time.gmtime(), self.currenthumidity, self.currenttemperature
            else:
                return time.gmtime(), None, None
        except:
            raise Exception("crashed: Sensor_DHT::read")            

    
class Sensor_PIR(object):
    """ Sensor_PIR is a passive infrared motion detector class of sensor """

    def __init__(self, pin, sensortype):
        try:
            Sensors.__init__(self)
            self.pin = pin
            self.sensortype = sensortype
            self.events = 0
            self.count = 0
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.pin, GPIO.IN)
            return
        except:
            raise Exception("crashed: Sensor_PIR::__init__")

    def __del__(self):
        Sensors.__del__(self)
        return
    
    def read(self):
        try:
            return time.gmtime(), GPIO.input(self.pin)
        except:
            raise Exception("crashed: Sensor_PIR::read")

    def get_count(self):
        try:
            return self.count
        except:
            raise Exception("crashed: Sensor_PIR::get_events")

    def reset_count(self):
        try:
            #nonlocal _events
            self.count = 0
            return
        except:
            raise Exception("crashed: Sensor_PIR::reset_events")

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
        try:
            self.count = self.count + 1
            return
        except:
            GPIO.remove_event_detect(self.pin)
            raise Exception("crashed: Sensor_PIR::standard_callback")
        


