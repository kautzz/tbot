#!/usr/bin/env python

import time

import blinkt


blinkt.set_clear_on_exit()

blinkt.set_pixel(0, 255, 255, 255, 1)
blinkt.set_pixel(1, 255, 255, 255, 1)
blinkt.set_pixel(2, 255, 255, 255, 1)
blinkt.set_pixel(3, 255, 255, 255, 1)
blinkt.set_pixel(4, 255, 255, 255, 1)
blinkt.set_pixel(5, 255, 255, 255, 1)
blinkt.set_pixel(6, 255, 255, 255, 1)
blinkt.set_pixel(7, 255, 255, 255, 1)

blinkt.show()
while True:
    pass
