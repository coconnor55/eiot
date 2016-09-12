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

debugthis=False

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
        self.pin = int(args['pin'])
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
        self.currenthumidity, self.currenttemperature = Adafruit_DHT.read_retry(self.sensortype, self.pin)
        if self.currenthumidity is not None and self.currenttemperature is not None:
            return time.gmtime(), self.currenthumidity, self.currenttemperature
        else:
            return time.gmtime(), None, None

    
class Sensor_PIR(Sensors):
    """ Sensor_PIR is a passive infrared motion detector class of sensor """
    PIR = {
        'PIR_HC_SR501' : 1
        }
    
    def __init__(self, **args):
        Sensors.__init__(self)
        self.pin = int(args['pin'])
        self.sensortype = args['type']

        # rising edge
        self.rising_count = 0
        self.rising_time = 0
        self._rising_callback = None

        # falling edge
        self.falling_count = 0
        self.falling_time = 0
        self._falling_callback = None

        # motion
        self._motion_callback = None

        # GPIO setup
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(int(self.pin), GPIO.IN)
        GPIO.add_event_detect(self.pin, GPIO.BOTH, callback=self._edge_change)

    def __enter__(self):
        Sensors.__enter__(self)
        return self

    def __exit__(self, type, value, traceback):
        Sensors.__exit__(self, type, value, traceback)

    def __del__(self):
        Sensors.__del__(self)
    
    def read(self):
        try:
            return time.gmtime(), GPIO.input(self.pin), self.rising_count, self.falling_count
        except:
            raise Exception("crashed: Sensor_PIR::read")

    def reset_count(self):
        self.rising_count = 0
        self.falling_count = 0

    def register_callback(self, **args):
        if 'rising' in args: self._rising_callback = args['rising']
        if 'falling' in args: self._falling_callback = args['falling']
        if 'motion' in args: self._motion_callback = args['motion']
        
    def _edge_change(self, pin):
        if GPIO.input(pin) == 1:
            # GPIO.RISING
            self.rising_count += 1
            self.rising_time = int(time.time()*1000)
            if self._rising_callback is not None: self._rising_callback(self, pin)

        elif GPIO.input(pin) != 1:
            # GPIO.FALLING
            self.falling_count += 1
            self.falling_time = int(time.time()*1000)
            if self._falling_callback is not None: self._falling_callback(self, pin)
            width = self.falling_time - self.rising_time
            if self._motion_callback is not None: self._motion_callback(self, pin, width)

class SensorState():
    states = ['sleep', 'awake', 'alert', 'alarm']

    def __init__(self, pir, callback=None):
        self.state = 'sleep'
        self.sleep_time = 0
        self.awake_time = 0
        self.alert_time = 0
        self.alarm_time = 0
        self.sleep_after = 60 * 1000
        self.alert_after = 5 * 1000
        self.alarm_after = 5 * 1000
        self.pir = pir
        self.callback = callback

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass
    
    def __del__(self):
        pass

    def _enter_sleep(self):
        if debugthis: print ("entering sleep")
        self.pir.reset_count()
        self.sleep_time = int(time.time()*1000)
        self.state = 'sleep'
        if self.callback is not None: self.callback(self, self.state)

    def _enter_awake(self):
        if debugthis: print ("entering awake")
        self.awake_time = int(time.time()*1000)
        self.state = 'awake'
        if self.callback is not None: self.callback(self, self.state)

    def _enter_alert(self):
        self.alert_time = int(time.time()*1000)
        self.state = 'alert'
        if self.callback is not None: self.callback(self, self.state)

    def _enter_alarm(self):
        self.alert_time = int(time.time()*1000)
        self.state = 'alarm'
        if self.callback is not None: self.callback(self, self.state)

    def evaluate(self):
        current_time = int(time.time()*1000)

        # go back to sleep if there is no activity 
        if self.state is not 'sleep' and (current_time - self.pir.rising_time > self.sleep_after
                and current_time - self.pir.falling_time > self.sleep_after):
            return self._enter_sleep()
        
        # remain asleep or transition to awake at first activity
        if self.state is 'sleep':
            if self.pir.rising_count > 0 or self.pir.falling_count > 0:
                return self._enter_awake()

        # remain awake or transition to alert if more activity
        elif self.state is 'awake':
            if (self.pir.rising_count > 2 or self.pir.falling_count > 2
                    or (self.pir.rising_count > self.pir.falling_count
                    and current_time - self.awake_time >= self.alert_after)):
                return self._enter_alert()
            
        # remain alert or transition to alarm if more activity
        elif self.state is 'alert':
            if (self.pir.rising_count > 3 or self.pir.falling_count > 3
                    or (self.pir.rising_count > self.pir.falling_count
                    and current_time - self.alert_time >= self.alarm_after)):
                return self._enter_alarm()
            
            
        
