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
if simulation == True:
    simulation_pretty = 'SIM'
else:
    simulation_pretty = 'HOT'

market = ''
ticker = ''
wallets = ''
last_trade = ''
open_orders = ''
data_fetch_time = time.time()


# Command Line Options
parser = argparse.ArgumentParser(description='tbot')
parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")

args = parser.parse_args()
if args.verbose:
    log.basicConfig(level=log.INFO, format='%(asctime)s - %(levelname)s: %(message)s')


# Just A Gimmick, Prints A Nice Header To The CLI
def print_header():
    os.system('cls' if os.name == 'nt' else 'clear')
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
    print(secrets.ex + ' / ' + symbol + ' / ' + simulation_pretty + ' / ' + data_age_str)
    print('-----------------------------------\n')


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
    trades = exchange.fetch_my_trades(symbol)
    last_trade = trades[len(trades)-1]
    del last_trade['info']


# Get All Open Orders
def get_open_orders(exchange):
    global open_orders
    open_orders = exchange.fetch_open_orders(symbol)
    for list_element in open_orders:
	       del list_element['info']


# Update the symbols ticker
def get_ticker(exchange):
    global ticker
    ticker = exchange.fetch_ticker(symbol)
    del ticker['info']


# Update your wallet balance
def get_wallet(exchange):
    global wallets
    wallets = exchange.fetch_balance()
    del wallets['info']


# Get Info About The Symbol About To Be Traded
def get_market(exchange):
    global market
    markets = exchange.load_markets()
    market = markets[symbol]


# Get All Infos Needed From Exchange
def fetch_all(exchange):
    global data_fetch_time
    data_fetch_time = time.time()
    print_header()
    print('Fetching Data...')
    get_ticker(exchange)
    get_market(exchange)
    get_last_trade(exchange)
    get_wallet(exchange)
    get_open_orders(exchange)
    print('Done!')


# Show a summary of the most important Details
def show_summary():
    print_header()
    print('Here Is A Summary Of Your Data:')
    print('Fetched At: ' + time.ctime(data_fetch_time) + '\n')

    wallet_summary = wallets
    del wallet_summary['free']
    del wallet_summary['used']
    del wallet_summary['total']
    print('Your Wallet Balances:' + dump(wallet_summary))

    print('Open Orders: ' + dump(open_orders))

    print('Your Last Trade:' + dump(last_trade))

    market_summary = market
    del market_summary['tiers']
    print('Market Info: ' + dump(market_summary))

    print('Ticker: ' + dump(ticker))

# Buy Or Sell Crypto At Current Market Price
def post_order(exchange, side, type, amount, price, cost):
    print('\n===================================\n')
    print('Posting Order: ' + type + ' ' + side + ' ' + str(amount) + ' ' + symbol_single[0] + ' @ ' + str(price) + ' ' + symbol_single[1])
    print('Total: ' + str(cost) + ' ' + symbol_single[1] + '\n')

    if simulation == False:
        order = exchange.createOrder(symbol, type, side, amount, price)
        print(dump(order))
    else:
        print('You Are Running A Simulation! Nothing Happened...')

    play_notification_sound()


def auto_trade(exchange):
    exchange_features = exchange.has
    print('Exchange Features:' + dump(exchange_features))

    print("fetchOpenOrders")
    print(dump(exchange.fetch_open_orders()))

    print("fetchClosedOrders")
    print(dump(exchange.fetch_closed_orders()))

    print("fetchClosedOrder")
    print(dump(exchange.fetch_closed_order('61648992890')))

    print("fetchOpenOrder")
    print(dump(exchange.fetch_open_order('61585221601')))

    input('Press Any Key To Continue...')


# Set Up Auto Trading Parameters
def manual_trade(exchange):
    print_header()

    print('Setting Up A Manual Trade\n')
    print('Current Prices:')
    print(str(ticker['bid']) + ' Bid / ' + str(ticker['ask']) + ' Ask' + '\n')
    print('Current Wallet Balances:')
    print(str(wallets['free'][symbol_single[0]]) + ' ' + symbol_single[0] + ' (used ' + str(wallets['used'][symbol_single[0]]) + ')')
    print(str(wallets['free'][symbol_single[1]]) + ' ' + symbol_single[1] + ' (used ' + str(wallets['used'][symbol_single[1]]) + ')' + '\n')

    # Manual Trade Menu
    def setup_manual_trade(exchange):
        print('===================================\n')
        print('[1] Buy ' + symbol_single[0])
        print('[2] Sell ' + symbol_single[0])
        print('-----------------------------------')
        print('[Q] Back To Main Menu\n')

        manual_trade_opt = input('Select An Option: ')

        # Manual Buy
        if manual_trade_opt == '1':
            min_buy = market['limits']['amount']['min'] * ticker['ask']
            print('\nMinimum Buy Is: ' + str(min_buy) + ' ' + symbol_single[1])

            if wallets['free'][symbol_single[1]] < min_buy:
                print('\n> Your ' + symbol_single[1] + ' Balance Is Insufficient, Try Selling ' + symbol_single[0] + '! \n')
                setup_manual_trade(exchange)

            else:
                buy_in = float(input('How Much Do You Want To Invest? ' + symbol_single[1] + ': '))
                # TODO check for sufficient funds!

                print('')
                print('[3] Market Order @ ' + str(ticker['ask']))
                print('[4] Limit Order')
                print('-----------------------------------')
                print('[Q] Back To Main Menu\n')
                order_type = input('Select An Option: ')

                if order_type == '3':
                    post_order(exchange, 'buy', 'market', buy_in/ticker['ask'], ticker['ask'], buy_in)
                elif order_type == '4':
                    desired_price = float(input('At What Price Do You Want To Buy? ' + symbol_single[1] + ': '))
                    post_order(exchange, 'buy', 'limit', buy_in/desired_price, desired_price, buy_in)
                elif order_type == 'Q' or order_type == 'q':
                    return

        # Manual Sell
        elif manual_trade_opt == '2':
            min_sell = market['limits']['amount']['min']
            print('\nMinimum Sell Is: ' + str(min_sell) + ' ' + symbol_single[0])

            if wallets['free'][symbol_single[0]] < min_sell:
                print('\n> Your ' + symbol_single[0] + ' Balance Is Insufficient, Try Buying ' + symbol_single[0] + '! \n')
                setup_manual_trade(exchange)

            else:
                sell_out = float(input('How Much Do You Want To Sell? ' + symbol_single[0] + ': '))
                # TODO check for sufficient funds!

                print('')
                print('[3] Market Order @ ' + str(ticker['bid']))
                print('[4] Limit Order')
                print('-----------------------------------')
                print('[Q] Back To Main Menu\n')
                order_type = input('Select An Option: ')

                if order_type == '3':
                    post_order(exchange, 'sell', 'market', sell_out, ticker['bid'], sell_out*ticker['bid'])
                elif order_type == '4':
                    desired_price = float(input('At What Price Do You Want To Sell? ' + symbol_single[1] + ': '))
                    post_order(exchange, 'sell', 'limit', sell_out, desired_price, sell_out*desired_price)
                elif order_type == 'Q' or order_type == 'q':
                    return

                #def post_order(exchange, side, type, amount, price, cost):
                #post_order(exchange, 'sell', sell_out, ticker['bid'], sell_out*ticker['bid'])

        elif manual_trade_opt == 'Q' or manual_trade_opt == 'q':
            return

        else:
            print('\n> Invalid Answer! Read And Repeat! \n')
            setup_manual_trade(exchange)

        # TODO option for another manual trade
        input('\n> Press RETURN To Continue...')
        fetch_all(exchange)

    setup_manual_trade(exchange)


# Find Crypto Currencies on Exchange that are low minimum buy-in but rather high volume
# Good for debugging
def find_cheap_tradepairs(exchange):
    print_header()

    tickers = exchange.fetch_tickers()
    tickers_tuples = list(ccxt.Exchange.keysort(tickers).items())

    markets = exchange.load_markets()
    tuples = list(ccxt.Exchange.keysort(markets).items())

    # output a table of all markets
    print('{:<10} {:<7} {:<7} {:<7} {:<10} {:<10} {:<6} {:<13} {:<13}'.format('symbol', 'taker', 'maker', 'limit', 'bid', 'buyin', '%', 'vol', 'vol/buyin'))
    for (k, v) in tuples:
        if v['quote'] == 'USD':
            if round(tickers[v['symbol']]['bid']*v['limits']['amount']['min'],6) <= 0.5:
                if round(tickers[v['symbol']]['baseVolume']) >= 5000:
                    if round(tickers[v['symbol']]['baseVolume']/tickers[v['symbol']]['bid']*v['limits']['amount']['min'],4) >= 50:
                        print('{:<10} {:<7} {:<7} {:<7} {:<10} {:<10} {:<6} {:<13} {:<13}'.format(v['symbol'], v['taker'], v['maker'], v['limits']['amount']['min'], tickers[v['symbol']]['bid'], round(tickers[v['symbol']]['bid']*v['limits']['amount']['min'],6), round(tickers[v['symbol']]['percentage'],3), round(tickers[v['symbol']]['baseVolume'],3), round(tickers[v['symbol']]['baseVolume']/tickers[v['symbol']]['bid']*v['limits']['amount']['min'],4)))


# This Shows The Main Menu In The CLI
def menu(exchange):
    print_header()
    print('[0] Refetch All Data')
    print('[1] Show Summary')
    print('[2] Set Up A Manual Trade')
    print('[3] Start Auto Trading')
    print('[4] Discover Cheap Trade Pairs')
    print('-----------------------------------')
    print('[Q] Quit\n')
    print('[T] Features In Test\n')

    opt = input('Select An Option: ')
    print('')

    if opt == '0':
        fetch_all(exchange)

    elif opt == '1':
        show_summary()
        input('Press RETURN To Continue...')

    elif opt == '2':
        manual_trade(exchange)

    elif opt == '3':
        print_header()
        print('> This Aint Done Yet...')
        input('> Press RETURN To Continue...')

    elif opt == '4':
        find_cheap_tradepairs(exchange)
        input('\n> Press RETURN To Continue...')

    elif opt == 'Q' or opt == 'q':
        os.system('cls' if os.name == 'nt' else 'clear')
        sys.exit('You Quit The Program!\nBruv You Gotta Spend Money To Make Money...\n')


    elif opt == 'T' or opt == 't':
        print('Feature In Development')
        time.sleep(3)
        auto_trade(exchange)
        print('Done!')
        time.sleep(3)


    else:
        print_header()
        print('> Invalid Answer! Read And Repeat!')
        input('> Press RETURN To Continue...')


def main():
    print_header()

    # Log In To Exchange
    print('Connecting To Crypto Exchange...')
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


if __name__ == "__main__":
    main()

print('')
print('[ ☑ End Of Program ]')
