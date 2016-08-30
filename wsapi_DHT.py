""" Module Cameras """
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
from flask import Flask
import Adafruit_DHT

mysensor = Adafruit_DHT.DHT11
mypin = 14
myDHT = Sensor_DHT(mypin, mysensor)
    
app = flask.Flask(__name__)

@app.route('/')
def index():
    return 'Easy IOT Temperature/Humidity'

@app.route("/eiot/api1.0/temperature/")
def get_temperature():
    humidity, temperature = read_sensor(mysensor, mypin)
    return str(temperature)

@app.route("/eiot/api1.0/temperature/<string:units>/")
def get_temperature_units(units):
    humidity, temperature = read_sensor(mysensor, mypin)
    if units.lower() == "c":
        return str(temperature)
    if units.lower() == "f":
        return str((temperature * 1.8) + 32)
    if units.lower() == "k":
        return str(temperature + 273)

@app.route("/eiot/api1.0/humidity/")
def get_humidity():
    humidity, temperature = myDHT.read(mysensor, mypin)
    return str(humidity)

@app.route("/exit/")
def exit():
    func = request.environ.get("werkzeug.server.shutdown")
    if func is not None:
        func()
    return "app.exit"
    
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
