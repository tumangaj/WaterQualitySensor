import RPi.GPIO as GPIO
import time
import os
import http.client as  httplib
import urllib
import board
import busio
import digitalio
import adafruit_apds9960.apds9960
from adafruit_debouncer import Debouncer

button_input1 = digitalio.DigitalInOut(board.D23)
button_input1.switch_to_input(pull=digitalio.Pull.UP)
button1 = Debouncer(button_input1)

i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_apds9960.apds9960.APDS9960(i2c)
sensor.enable_color = True

class PushoverSender:
    def __init__(self, user_key, api_key):
        self.user_key = user_key
        self.api_key = api_key

    def send_notification(self, text):
        conn = httplib.HTTPSConnection("api.pushover.net:443")
        post_data = {'user': self.user_key, 'token': self.api_key, 'message': text}
        conn.request("POST", "/1/messages.json",
                     urllib.parse.urlencode(post_data), {"Content-type": "application/x-www-form-urlencoded"})
        # print(conn.getresponse().read())

def get_key(filename):
    with open(filename) as f:
        key = f.read().strip()
    return key

def main():
    # Get Pushover keys from files
    user_key = get_key(os.path.join(os.path.dirname(__file__), 'user.key'))
    api_key = get_key(os.path.join(os.path.dirname(__file__), 'apitoken.key'))

    pushover_sender = PushoverSender(user_key, api_key)
    #for i in range(5):
    #	pushover_sender.send_notification('heyyy')
    while True:
        button1.update()
        r, g, b, c = sensor.color_data
        print('Red: {0}, Green: {1}, Blue: {2}, Clear: {3}'.format(r, g, b, c))
        if c >= 30 and button1.fell:
            pushover_sender.send_notification('Water Quality Good')
        if c >= 20 and c < 30 and button1.fell:
            pushover_sender.send_notification('Water Quality Poor')
        if c < 20 and button1.fell:
            pushover_sender.send_notification('Water Quality Very Poor')

main()
