#
#GNU General Public License v3.0
#Permissions of this strong copyleft license are conditioned on making available
#complete source code of licensed works and modifications, which include larger
#works using a licensed work, under the same license. Copyright and license
#notices must be preserved. Contributors provide an express grant of patent
#rights.
#

import json
from urllib.request import urlopen
import RPi.GPIO as GPIO
GPIO.setwarnings(False)
import time

GPIO.setmode(GPIO.BOARD) #sets pin mapping to board locations on Raspberry Pi 3b
# add more/different economizer control points here
damper = 7
y1 = 11
y2 = 13
fan = 15
GPIO.setup(damper, GPIO.OUT, initial=GPIO.HIGH) #sets pin for damper as output in normal economizermode
GPIO.setup(y1, GPIO.OUT, initial=GPIO.HIGH) 
GPIO.setup(y2, GPIO.OUT, initial=GPIO.HIGH) 
GPIO.setup(fan, GPIO.OUT, initial=GPIO.HIGH) 

#GPIO.output(damper, GPIO.LOW) #smoke mode operation
#GPIO.output(damper, GPIO.HIGH) #normal economizer operation

def load_config():
    try:
        from config import CONFIG
    except ImportError:
        raise Exception("Please copy config.py.example to config.py and edit config.py to include your config info.")
    # config validation
    assert CONFIG["low_act"] < CONFIG["hi_act"]
    #CONFIG["distance"] = "25"  # should this be user configurable? --Yes--
    return CONFIG


def request_pm25(config):
    base = "https://www.airnowapi.org/aq/observation/zipCode/current/"
    template = base + "?format=application/json&zipCode={zipcode}&distance={distance}&API_KEY={token}"
    url = template.format(**config)
    response = urlopen(url, timeout=10)
    if response.status == 200:
        pm25 = parse_pm25(response)
        return pm25
    else:
        raise ConnectionError("%s returned %i, body: %s" % (base, response.status, response.read()))


def parse_pm25(response):
    body = response.read()
    data = json.loads(body)
    pm25aqi = None
    for entry in data:  # entries include "O3", "PM2.5"
        if entry["ParameterName"] == "PM2.5":
            pm25aqi = entry["AQI"]
            return pm25aqi
    if pm25aqi is None:
        raise ValueError("no PM2.5 data found, data: %s" % data)


if __name__ == "__main__":
    config = load_config()
    state = "normal economizer operation"
    try:
        pm25 = request_pm25(config)
        if pm25 >= config["hi_act"] and state == "normal economizer operation":
            #TODO: Add functions to bypass economizer operation
            GPIO.output(damper, GPIO.LOW) #smoke limiting economizer operation
            GPIO.output(y1, GPIO.LOW) #smoke limiting economizer operation
            GPIO.output(y2, GPIO.LOW) #smoke limiting economizer operation
            GPIO.output(fan, GPIO.LOW) #smoke limiting economizer operation
            state = "smoke limiting economizer operation"
        if pm25 < config["low_act"]:
            state = "normal economizer operation"
            GPIO.output(damper, GPIO.HIGH) #normal economizer operation
            GPIO.output(y1, GPIO.HIGH) #normal economizer operation
            GPIO.output(y2, GPIO.HIGH) #normal economizer operation
            GPIO.output(fan, GPIO.HIGH) #normal economizer operation
        print("pm25: %s" % pm25)
        print("hi_act: %s" %config["hi_act"])
        print("low_act: %s" %config["low_act"])
        print("would set to %s" % state)
    except Exception as e:
        # request or parsing failed -- probably a transient network error
        # if this were in a loop, we should log and retry
        raise e
    
    #GPIO.cleanup() #resets all pins to inputs
    