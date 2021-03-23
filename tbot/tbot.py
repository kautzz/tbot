# coding=utf-8
#!/usr/bin/env python3

"""
tbot (WIP)
"""

import time
import datetime
import simpleaudio as sa

import logging as log
import argparse
from configparser import ConfigParser

import ccxt
import secrets

# Read Config File
config = ConfigParser()
config.read('settings.ini')

# Command Line Options
parser = argparse.ArgumentParser(description='tbot')
parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")

args = parser.parse_args()
if args.verbose:
    log.basicConfig(level=log.INFO, format='%(asctime)s - %(levelname)s: %(message)s')

# Plays a notification sound if enabled in config
def play_notification_sound():
    log.info('Playing Notification Sound If Enabled')
    if config.getboolean('main', 'sound_enabled') == True:
        wave_obj = sa.WaveObject.from_wave_file("src/notification.wav")
        play_obj = wave_obj.play()
        play_obj.wait_done()


def dump(*args):
    print(' '.join([str(arg) for arg in args]))


def main():
    print('Selecting Exchange ' + secrets.ex)

    exchange_class = getattr(ccxt, secrets.ex)
    exchange = exchange_class({
        'apiKey': secrets.apiKey,
        'secret': secrets.apiSec,
        'timeout': 30000,
        'enableRateLimit': True,
    })

    print(exchange.fetch_status())
    print('')

    print(exchange.has)
    print('')

    markets = exchange.load_markets()
    tuples = list(ccxt.Exchange.keysort(markets).items())

    # output a table of all markets
    dump('{:<15} {:<15} {:<15} {:<15}'.format('id', 'symbol', 'base', 'quote'))
    for (k, v) in tuples:
        dump('{:<15} {:<15} {:<15} {:<15}'.format(v['id'], v['symbol'], v['base'], v['quote']))

    print('')
    print(exchange.fetch_tickers(['IOTA/USD', 'BTC/USD']))
    print('')
    print(exchange.fetch_ticker('DOG/USD'))

    print('')
    print(exchange.fetch_balance())

    print('')
    print(exchange.fetch_my_trades())


if __name__ == "__main__":
    main()

print('')
print('[ ☑ End Of Program ]')
