"""
tbot candy.py
All eyecandy functions are here. This includes:

* CLI Nerdery
* PiOLED Display Stuff
* Blinkt! LED Bar Stuff
* Audio Notifications

"""

import time
import datetime
import simpleaudio as sa
from configparser import ConfigParser

# Read Config File
config = ConfigParser()
config.read('settings.ini')

got_pi = False
got_oled = False
got_blinkt = False

oled = 0
image = 0
draw = 0
font = 0
blinkt = 0


# Prints A Nice Header To The CLI
def cli_header(ex, sym, sim, data_fetch_time):

    # TODO uncomment in production
    #os.system('cls' if os.name == 'nt' else 'clear')
    data_age = round(time.time() - data_fetch_time)
    data_age_str = str(datetime.timedelta(seconds=data_age))

    print(r"""
   __  __          __
  / /_/ /_  ____  / /_
 / __/ __ \/ __ \/ __/
/ /_/ /_/ / /_/ / /_
\__/_.___/\____/\__/__
  ____ _/ / /  / /_/ /_  ___
 / __ `/ / /  / __/ __ \/ _ \
/ /_/ / / /  / /_/ / / /  __/
\__,_/_/_/   \__/_/ /_/\___/
  ____________  ______  / /_____  _____
 / ___/ ___/ / / / __ \/ __/ __ \/ ___/
/ /__/ /  / /_/ / /_/ / /_/ /_/ (__  )
\___/_/   \__, / .___/\__/\____/____/
         /____/_/

    """)
    print('-----------------------------------')
    print(ex + ' / ' + sym + ' / ' + sim + ' / ' + data_age_str)
    print('-----------------------------------\n')


# If we're on a Pi and have the PiOLED display attached
# include libs and do basic setup
def setup_oled():

    global oled
    global image
    global draw
    global font

    from board import SCL, SDA
    import busio
    from PIL import Image, ImageDraw, ImageFont
    import adafruit_ssd1306

    i2c = busio.I2C(SCL, SDA)
    oled = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c)

    oled.fill(0)
    oled.show()

    image = Image.new("1", (oled.width, oled.height))
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()

    print('Enabled PiOLED!')


# If we're on a Pi and have the BLINKT! LED bar attached
# include libs and do basic setup
def setup_blinkt():

    global blinkt

    import blinkt
    blinkt.set_clear_on_exit()
    print('Enabled BLINKT!')


# See if we're running things on a pi
# and have PiOlED display or BLINKT! LED bar attached
def detect_hardware():

    global got_oled
    global got_blinkt

    try:
        with open('/proc/device-tree/model', 'r') as device_model:
            model = device_model.read()
            if 'Raspberry Pi' in model:
                got_pi = True
                print('Running On RaspberryPi!')

    except Exception as e:
        print(e)

    if got_pi and config.getboolean('output', 'oled_attached'):
        got_oled = True
        setup_oled()

    if got_pi and config.getboolean('output', 'blinkt_attached'):
        got_blinkt = True
        setup_blinkt()


# Litte greeting on the oled display and LED bar (if attached)
def welcome_message():

    if got_blinkt:
        for i in range(blinkt.NUM_PIXELS):
            blinkt.set_pixel(i, 0, 255, 0, 0.1)
            blinkt.show()

    if got_oled:
        oled.poweron()
        draw.rectangle((0, 0, oled.width, oled.height), outline=0, fill=0)

        draw.text((0, 0), '--------------------', font=font, fill=255)
        draw.text((0, 8), 'tbot all the', font=font, fill=255)
        draw.text((0, 16), 'cryptos', font=font, fill=255)
        draw.text((0, 25), '--------------------', font=font, fill=255)

        oled.image(image)
        oled.show()


def menu(ex, sym, sim, data_fetch_time):

    if got_blinkt:
        for i in range(blinkt.NUM_PIXELS):
            blinkt.set_pixel(i, 255, 255, 255, 0.1)
        blinkt.show()

    if got_oled:
        data_age = round(time.time() - data_fetch_time)
        data_age_str = str(datetime.timedelta(seconds=data_age))

        oled.poweron()
        draw.rectangle((0, 0, oled.width, oled.height), outline=0, fill=0)

        draw.text((0, 0), '--------------------', font=font, fill=255)
        draw.text((0, 8), ex + ' / ' + sym, font=font, fill=255)
        draw.text((0, 16), sim + ' / ' + data_age_str, font=font, fill=255)
        draw.text((0, 25), '--------------------', font=font, fill=255)

        oled.image(image)
        oled.show()


def bot_buy():
    if got_blinkt:
        blinkt.set_pixel(0, 0, 255, 0, 0.1)
        blinkt.show()

def bot_sell():
    if got_blinkt:
        blinkt.set_pixel(0, 255, 0, 0, 0.1)
        blinkt.show()

def bot_check_order():
    if got_blinkt:
        if blinkt.get_pixel(7)[3] > 0.0:
            blinkt.set_pixel(7, 255, 255, 255, 0)
        else:
            blinkt.set_pixel(7, 255, 255, 255, 0.1)

        blinkt.show()


# Clears and turns off oled display and LED bar (if attached)
def clear():

    if got_blinkt:
        for x in range(blinkt.NUM_PIXELS):
            blinkt.set_pixel(x, 0, 0, 0, 0)
        blinkt.show()

    if got_oled:
        oled.fill(0)
        oled.show()
        oled.poweroff()


# Plays a notification sound (if enabled in config)
def notification_sound():
    if config.getboolean('output', 'sound_enabled') == True:
        wave_obj = sa.WaveObject.from_wave_file("src/notification.wav")
        play_obj = wave_obj.play()
        play_obj.wait_done()
