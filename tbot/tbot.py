# coding=utf-8
#!/usr/bin/env python3

"""
tbot (WIP)
"""

import time
import datetime
import simpleaudio as sa
import json
import os
import sys

import logging as log
import argparse
from configparser import ConfigParser

import ccxt
import secrets


# Read Config File
config = ConfigParser()
config.read('settings.ini')


# Global Variables
symbol = config.get('main', 'symbol')
symbol_single = symbol.split('/', 1)

market = ''
ticker = ''
wallets = ''
last_trade = ''


# Command Line Options
parser = argparse.ArgumentParser(description='tbot')
parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")

args = parser.parse_args()
if args.verbose:
    log.basicConfig(level=log.INFO, format='%(asctime)s - %(levelname)s: %(message)s')


def print_header():
    os.system('cls' if os.name == 'nt' else 'clear')

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



# Plays a notification sound if enabled in config
def play_notification_sound():
    log.info('Playing Notification Sound If Enabled')
    if config.getboolean('main', 'sound_enabled') == True:
        wave_obj = sa.WaveObject.from_wave_file("src/notification.wav")
        play_obj = wave_obj.play()
        play_obj.wait_done()


# Format Dicts For Output In CLI
def dump(dict):
    return '\n' + '\n' + json.dumps(dict, indent=4, default=str) + '\n' + '\n'


# Get your last trade from the exchange and drop the info part
def get_last_trade(exchange):
    global last_trade
    trades = exchange.fetch_my_trades()
    last_trade = trades[len(trades)-1]
    del last_trade['info']


# Update the symbols ticker
def get_ticker(exchange):
    global ticker
    ticker = exchange.fetch_ticker(symbol)


# Update your wallet balance
def get_wallet(exchange):
    global wallets
    wallets = exchange.fetch_balance()


# Get Info About The Symbol About To Be Traded
def get_market(exchange):
    global market
    markets = exchange.load_markets()
    market = markets[symbol]


# Show a summary of the most important Details
def show_recap():
    print('Your Last Trade:' + dump(last_trade))
    print('Your Wallet Balances:' + dump(wallets['total']))


# Set Up Auto Trading Parameters
def auto_trading_setup():
    print_header()

    print('Setting Up Automatic Trading For Symbol: ' + symbol + '\n')
    print('Current Prices:')
    print(str(ticker['bid']) + ' Buy / ' + str(ticker['ask']) + ' Sell' + '\n')
    print('Current Wallet Balances:')
    print(str(wallets['total'][symbol_single[0]]) + ' ' + symbol_single[0])
    print(str(wallets['total'][symbol_single[1]]) + ' ' + symbol_single[1] + '\n')

    def sel_starting_operation():
        starting_operation = input('Do You Want To [Q]uit or Start With [B]uying or [S]elling ' + symbol_single[0] + '? ')

        if starting_operation == 'B' or starting_operation == 'b':
            min_buy = round(market['limits']['amount']['min'] * ticker['bid'], 2)
            print('Minimum Buy Is: ' + str(min_buy) + ' ' + symbol_single[1])

            if wallets['total'][symbol_single[1]] < min_buy:
                print('\n  Your ' + symbol_single[1] + ' Balance Is Insufficient, Try Selling ' + symbol_single[0] + '! \n')
                sel_starting_operation()

            else:
                buy_in = float(input('How Much Do You Want To Invest? ' + symbol_single[1] + ': '))
                print(str(buy_in))

        elif starting_operation == 'S' or starting_operation == 's':
            min_sell = market['limits']['amount']['min']
            print('Minimum Sell Is: ' + str(min_sell) + ' ' + symbol_single[0])

            if wallets['total'][symbol_single[0]] < min_sell:
                print('\n  Your ' + symbol_single[0] + ' Balance Is Insufficient, Try Buying ' + symbol_single[0] + '! \n')
                sel_starting_operation()

            else:
                sell_out = float(input('How Much Do You Want To Sell? ' + symbol_single[0] + ': '))
                print(str(sell_out))

        elif starting_operation == 'Q' or starting_operation == 'q':
            sys.exit('User Quit The Program')


        else:
            print('Invalid Answer! Read And Repeat!')
            sel_starting_operation()

    sel_starting_operation()
    print('Auto Trading Setup Complete!')


def main():
    print_header()

    # Log In To Exchange
    print('Connecting To Crypto Exchange: ' + secrets.ex)
    exchange_class = getattr(ccxt, secrets.ex)
    exchange = exchange_class({
        'apiKey': secrets.apiKey,
        'secret': secrets.apiSec,
        'timeout': 30000,
        'enableRateLimit': True,
    })

    # Check Status Of Exchange & Continue When OK
    exchange_status = exchange.fetch_status()
    log.info('Exchange Status:' + dump(exchange_status))

    if exchange_status['status'] == 'ok':

        get_ticker(exchange)
        get_market(exchange)
        get_last_trade(exchange)
        get_wallet(exchange)

        if args.verbose:
            # Show Features Supported By Exchage
            exchange_features = exchange.has
            log.info('Exchange Features:' + dump(exchange_features))

        if args.verbose:
            # Show Symbol Details / Info
            log.info('Market Info For ' + symbol + ' :' + dump(market))

        show_recap()

        cont = input('Continue To Automatic Trading Setup? [Y/n] ')
        if cont == 'Y' or cont == 'y' or cont == '':
            auto_trading_setup()
        else:
            return

    else:
        log.critical('Exchange Status Is Not OK!')
        return

if __name__ == "__main__":
    main()

print('')
print('[ ☑ End Of Program ]')
