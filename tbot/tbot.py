# coding=utf-8
#!/usr/bin/env python3

"""
tbot (WIP)
"""

import time
import datetime
import simpleaudio as sa
import json

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


def dump(dict):
    return '\n' + '\n' + json.dumps(dict, indent=4, default=str) + '\n' + '\n'


def main():
    symbol = config.get('main', 'symbol')
    print('Connecting To: ' + secrets.ex)

    exchange_class = getattr(ccxt, secrets.ex)
    exchange = exchange_class({
        'apiKey': secrets.apiKey,
        'secret': secrets.apiSec,
        'timeout': 30000,
        'enableRateLimit': True,
    })

    exchange_status = exchange.fetch_status()
    print('Exchange Status:' + dump(exchange_status))

    exchange_features = exchange.has
    log.info('Exchange Features:' + dump(exchange_features))

    markets = exchange.load_markets()
    del markets[symbol]['tiers']
    print('Market Info For ' + symbol + ' :' + dump(markets[symbol]))

    ticker = exchange.fetch_ticker(symbol)
    print('Ticker For ' + symbol + ' :' + dump(ticker))

    wallets = exchange.fetch_balance()
    print('Your Wallet Balances:' + dump(wallets['total']))

    trades = exchange.fetch_my_trades()

    for list_element in trades:
        del list_element['info']

    last_trade = trades[len(trades)-1]

    print('Your Last Trade:' + dump(last_trade))


if __name__ == "__main__":
    main()

print('')
print('[ ☑ End Of Program ]')
