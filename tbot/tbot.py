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
simulation = config.getboolean('main', 'simulation')

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
    # TODO uncomment:
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


# Get All Infos Needed From Exchange
def fetch_all(exchange):
    print_header()
    print('Fetching Data From ' + secrets.ex + '...')
    get_ticker(exchange)
    get_market(exchange)
    get_last_trade(exchange)
    get_wallet(exchange)
    print('Done!')


# Show a summary of the most important Details
def show_recap():
    print_header()
    print('\nHere Is A Recap Of Your Last Actions:\n')
    print('Your Last Trade:' + dump(last_trade))
    print('Your Wallet Balances:' + dump(wallets['total']))


# Buy Or Sell Crypto At Current Market Price
def market_order(side, amount, price, cost):
    print("\nexchange.createOrder(symbol, 'market', 'buy', amount, price)")
    print('exchange.createOrder(' + symbol + ' market' + ' ' + side + ' ' + str(amount) + ' ' + str(price) + ')')
    print('cost/gain: ' + str(cost) + '\n')

    if simulation == False:
        print('ordered for real!')
        #order = exchange.createOrder(symbol, 'market', side, amount, price)
    else:
        print('simulated market order!')

    play_notification_sound()


# Set Up Auto Trading Parameters
def manual_trade():
    print_header()

    print('Setting Up Automatic Trading For Symbol: ' + symbol + '\n')
    print('Current Prices:')
    print(str(ticker['bid']) + ' Buy / ' + str(ticker['ask']) + ' Sell' + '\n')
    print('Current Wallet Balances:')
    print(str(wallets['total'][symbol_single[0]]) + ' ' + symbol_single[0])
    print(str(wallets['total'][symbol_single[1]]) + ' ' + symbol_single[1] + '\n')

    def setup_manual_trade():
        starting_operation = input('Do You Want To Go Back To [M]enu, [B]uy or [S]ell ' + symbol_single[0] + '? ')

        if starting_operation == 'B' or starting_operation == 'b':
            min_buy = round(market['limits']['amount']['min'] * ticker['bid'], 5)
            print('Minimum Buy Is: ' + str(min_buy) + ' ' + symbol_single[1])

            if wallets['total'][symbol_single[1]] < min_buy:
                print('\n> Your ' + symbol_single[1] + ' Balance Is Insufficient, Try Selling ' + symbol_single[0] + '! \n')
                setup_manual_trade()

            else:
                buy_in = float(input('How Much Do You Want To Invest? ' + symbol_single[1] + ': '))
                # TODO check for sufficient funds!
                market_order('buy', buy_in/ticker['bid'], ticker['bid'], buy_in)

        elif starting_operation == 'S' or starting_operation == 's':
            min_sell = market['limits']['amount']['min']
            print('Minimum Sell Is: ' + str(min_sell) + ' ' + symbol_single[0])

            if wallets['total'][symbol_single[0]] < min_sell:
                print('\n> Your ' + symbol_single[0] + ' Balance Is Insufficient, Try Buying ' + symbol_single[0] + '! \n')
                setup_manual_trade()

            else:
                sell_out = float(input('How Much Do You Want To Sell? ' + symbol_single[0] + ': '))
                market_order('sell', sell_out, ticker['ask'], sell_out*ticker['ask'])

        elif starting_operation == 'M' or starting_operation == 'm':
            return

        else:
            print('\n> Invalid Answer! Read And Repeat! \n')
            setup_manual_trade()

        # TODO option for another manual trade
        input('> Press RETURN To Continue...')

    setup_manual_trade()


# Find Crypto Currencies on Exchange that are low minimum buy-in but rather high volume
# Good for debugging
def find_low_entry_cryptos(exchange):
    print_header()

    tickers = exchange.fetch_tickers()
    tickers_tuples = list(ccxt.Exchange.keysort(tickers).items())

    markets = exchange.load_markets()
    tuples = list(ccxt.Exchange.keysort(markets).items())

    # output a table of all markets
    print('{:<25} {:<10} {:<10} {:<10} {:<10} {:<10} {:<10} {:<15} {:<15}'.format('symbol', 'taker', 'maker', 'limit', 'bid', 'buyin', '%', 'vol', 'vol/buyin'))
    for (k, v) in tuples:
        if v['quote'] == 'USD':
            if round(tickers[v['symbol']]['bid']*v['limits']['amount']['min'],6) <= 0.5:
                if round(tickers[v['symbol']]['baseVolume']) >= 5000:
                    if round(tickers[v['symbol']]['baseVolume']/tickers[v['symbol']]['bid']*v['limits']['amount']['min'],4) >= 50:
                        print('{:<25} {:<10} {:<10} {:<10} {:<10} {:<10} {:<10} {:<15} {:<15}'.format(v['symbol'], v['taker'], v['maker'], v['limits']['amount']['min'], tickers[v['symbol']]['bid'], round(tickers[v['symbol']]['bid']*v['limits']['amount']['min'],6), round(tickers[v['symbol']]['percentage'],3), round(tickers[v['symbol']]['baseVolume'],3), round(tickers[v['symbol']]['baseVolume']/tickers[v['symbol']]['bid']*v['limits']['amount']['min'],4)))


def menu(exchange):
    print_header()
    print("""
[0] Refetch All Data
[1] Show Recap Of Last Actions
[2] Manual Trade
[3] Continue Auto Trading
[4] Discover Low Entry Cryptos
------------------------------
[Q] Quit
    """)

    opt = input('Select An Option: ')
    print('')

    if opt == '0':
        fetch_all(exchange)
    elif opt == '1':
        show_recap()
        input('Press RETURN To Continue...')
    elif opt == '2':
        manual_trade()
    elif opt == '3':
        print_header()
        print('> This Aint Done Yet...')
        input('> Press RETURN To Continue...')
    elif opt == '4':
        find_low_entry_cryptos(exchange)
        input('> Press RETURN To Continue...')
    elif opt == 'Q' or opt == 'q':
        print_header()
        sys.exit('> You Quit The Program! Dude You Gotta Spend Money To Make Money...\n')
    else:
        print_header()
        print('> Invalid Answer! Read And Repeat!')
        input('> Press RETURN To Continue...')


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

        fetch_all(exchange)

        if args.verbose:
            # Show Features Supported By Exchage
            exchange_features = exchange.has
            log.info('Exchange Features:' + dump(exchange_features))

        if args.verbose:
            # Show Symbol Details / Info
            log.info('Market Info For ' + symbol + ' :' + dump(market))

        while True:
            menu(exchange)

    else:
        log.critical('Exchange Status Is Not OK!')
        return

if __name__ == "__main__":
    main()

print('')
print('[ ☑ End Of Program ]')
