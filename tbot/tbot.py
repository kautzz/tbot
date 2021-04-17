# coding=utf-8
#!/usr/bin/env python3

"""
tbot (WIP)
"""

import time
import json
import os
import sys

import logging as log
import argparse
from configparser import ConfigParser

import ccxt
import secrets

import candy
#import fetch
#import trade
#import bot
#import util


# Are we Running on a Raspberry Pi?
candy.detect_hardware()

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


# Log In To Exchange
print('Connecting To Crypto Exchange...')
exchange_class = getattr(ccxt, secrets.ex)
exchange = exchange_class({
    'apiKey': secrets.apiKey,
    'secret': secrets.apiSec,
    'timeout': 30000,
    'enableRateLimit': True,
})


# Format Dicts For Output In CLI
def dump(dict):
    return '\n' + '\n' + json.dumps(dict, indent=4, default=str) + '\n' + '\n'


# Get your last trade from the exchange and drop the info part
def get_last_trade():
    global last_trade
    trades = exchange.fetch_my_trades(symbol)
    last_trade = trades[len(trades)-1]
    del last_trade['info']


# Get All Open Orders
def get_open_orders():
    global open_orders
    open_orders = exchange.fetch_open_orders(symbol)
    for list_element in open_orders:
	       del list_element['info']


# Update the symbols ticker
def get_ticker():
    global ticker
    ticker = exchange.fetch_ticker(symbol)
    del ticker['info']


# Update your wallet balance
def get_wallet():
    global wallets
    wallets = exchange.fetch_balance()
    del wallets['info']


# Get Info About The Symbol About To Be Traded
def get_market():
    global market
    markets = exchange.load_markets()
    market = markets[symbol]


# Get All Infos Needed From Exchange
def fetch_all():
    global data_fetch_time
    data_fetch_time = time.time()
    candy.cli_header(secrets.ex, symbol, simulation_pretty, data_fetch_time)
    print('Fetching Data...')
    get_ticker()
    get_market()
    get_last_trade()
    get_wallet()
    get_open_orders()
    print('Done!')


# Show a summary of the most important Details
def show_summary():
    candy.cli_header(secrets.ex, symbol, simulation_pretty, data_fetch_time)
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


# Create an order to buy or sell Crypto
def post_order(side, type, amount, price, cost):
    print('\n===================================\n')
    print('Posting Order: ' + type + ' ' + side + ' ' + str(amount) + ' ' + symbol_single[0] + ' @ ' + str(price) + ' ' + symbol_single[1])
    print('Total: ' + str(cost) + ' ' + symbol_single[1] + '\n')

    if simulation == False:
        order = exchange.createOrder(symbol, type, side, amount, price)
        candy.notification_sound()
        return order

    else:
        print('You Are Running A Simulation! Nothing Happened...')
        return


def auto_trade():

    def bot_trade_complete_data(bot_trade):
        bot_trade['cost'] = bot_trade['price'] * bot_trade['amount']

        if bot_trade['type'] == 'limit':
            bot_trade['fee'] = market['maker'] * bot_trade['cost']
        elif bot_trade['type'] == 'market':
            bot_trade['fee'] = market['taker'] * bot_trade['cost']

        if bot_trade['side'] == 'buy':
            bot_trade['yield'] = (bot_trade['cost'] + bot_trade['fee']) * -1
        elif bot_trade['side'] == 'sell':
            bot_trade['yield'] = bot_trade['cost'] - bot_trade['fee']

        bot_trade['cumulative_profit'] = bot_trades[len(bot_trades)-2]['cumulative_profit'] + bot_trade['yield']

    def wait_for_order_to_complete():
        print("Waiting For Last Order To Complete ...")
        while True:
            try:
                last_order_status = exchange.fetch_closed_order(bot_trades[len(bot_trades)-1]['id'])
                if last_order_status['status'] == 'closed':
                    bot_trades[len(bot_trades)-1]['status'] = 'closed'
                    print('Filled:')
                    print(dump(bot_trades[len(bot_trades)-1]))
                    break
            except:
                pass

            time.sleep(5)


    get_ticker()

    # Decide Whether To Buy Or Sell First
    ## Get last 24h high and low to get the range of price movement
    range = ticker['high'] - ticker['low']
    print('24h high-low range: ' + str(range))
    print('24h avg price: ' + str(ticker['low'] + range / 2))
    print('current price: ' + str(ticker['close']))
    print('\nSetting Up Initial Trade!')

    if ticker['low'] + range / 2 >= ticker['close']: #todo set to >= for production
        print('Current Price Is On The LOW End Of The 24h Range! Buying First!')
        print('\nCurrent Wallet Balance: ' + str(wallets['free'][symbol_single[1]]) + ' ' + symbol_single[1] + ' (used ' + str(wallets['used'][symbol_single[1]]) + ')')

        min_buy = market['limits']['amount']['min'] * ticker['ask']
        print('Minimum Buy Is: ' + str(min_buy) + ' ' + symbol_single[1])

        if wallets['free'][symbol_single[1]] < min_buy:
            print('\n> Your ' + symbol_single[1] + ' Balance Is Insufficient, Try Selling ' + symbol_single[0] + '! \n')
            input('Press Any Key To Return To Main Menu...')
            return

        buy_in = float(input('How Much Do You Want To Invest? ' + symbol_single[1] + ': '))
        # TODO check for sufficient funds!
        order = post_order('buy', 'market', buy_in/ticker['ask'], ticker['ask'], buy_in)

    else:
        print('Current Price Is On The HIGH End Of The 24h Range! Selling First!')
        print('\nCurrent Wallet Balance: ' + str(wallets['free'][symbol_single[0]]) + ' ' + symbol_single[0] + ' (used ' + str(wallets['used'][symbol_single[0]]) + ')')

        min_sell = market['limits']['amount']['min']
        print('Minimum Sell Is: ' + str(min_sell) + ' ' + symbol_single[0])

        if wallets['free'][symbol_single[0]] < min_sell:
            print('\n> Your ' + symbol_single[0] + ' Balance Is Insufficient, Try Buying ' + symbol_single[0] + '! \n')
            input('Press Any Key To Return To Main Menu...')
            return

        sell_out = float(input('How Much Do You Want To Sell? ' + symbol_single[0] + ': '))
        # TODO check for sufficient funds!
        order = post_order('sell', 'market', sell_out, ticker['bid'], sell_out*ticker['bid'])

    bot_trades = [{
        'trade': 0,
        'id': order['id'],
        'timestamp': time.time(),
        'exchangetime': order['datetime'],
        'status': order['status'],
        'type': order['type'],
        'side': order['side'],
        'symbol': order['symbol'],
        'price': order['price'],
        'amount': order['amount'],
        'cost': 0.00,
        'fee': 0.00,
        'yield': 0.00,
        'cumulative_profit': 0.00
    }]
    bot_trade_complete_data(bot_trades[len(bot_trades)-1])
    wait_for_order_to_complete()


    input('Debugging Break! Press Any Key To Continue...')

    print('Press [CONTROL + C] To Stop Trading!')
    try:
        while True:
            if bot_trades[len(bot_trades)-1]['side'] == 'sell':
                print('\nLast: Sell. Next: Buy ...')

                spend = bot_trades[len(bot_trades)-1]['yield'] - bot_trades[len(bot_trades)-1]['yield'] * config.getfloat('auto_trade', 'bank_profit')
                print('Next Investment: ' + str(spend) + ' Banked: ' + str(bot_trades[len(bot_trades)-1]['yield'] * config.getfloat('auto_trade', 'bank_profit')))
                fee = market['maker'] * spend
                print('Next Fees: ' + str(fee))
                min_target_price = (spend - fee) / bot_trades[len(bot_trades)-1]['amount']
                print('Price No Profit: ' + str(min_target_price))
                target_price = min_target_price - min_target_price * config.getfloat('auto_trade', 'price_change')
                print('Price For Profit: ' + str(target_price))
                est_outcome = spend / target_price
                print('Outcome: ' + str(est_outcome))

                order = post_order('buy', 'limit', spend/target_price, target_price, spend)
                bot_trades.append({
                    'trade': bot_trades[len(bot_trades)-1]['trade']+1,
                    'id': order['id'],
                    'timestamp': time.time(),
                    'exchangetime': order['datetime'],
                    'status': order['status'],
                    'type': order['type'],
                    'side': order['side'],
                    'symbol': order['symbol'],
                    'price': order['price'],
                    'amount': order['amount'],
                    'cost': 0.00,
                    'fee': 0.00,
                    'yield': 0.00,
                    'cumulative_profit': 0.00
                })
                bot_trade_complete_data(bot_trades[len(bot_trades)-1])
                wait_for_order_to_complete()

            elif bot_trades[len(bot_trades)-1]['side'] == 'buy':
                print('\nLast: Buy. Next: Sell ...')

                spend = bot_trades[len(bot_trades)-1]['yield'] - bot_trades[len(bot_trades)-1]['yield'] * config.getfloat('auto_trade', 'bank_profit')
                print('Next Investment: ' + str(spend) + ' Banked: ' + str(bot_trades[len(bot_trades)-1]['yield'] * config.getfloat('auto_trade', 'bank_profit')))
                fee = market['maker'] * spend * -1
                print('Next Fees: ' + str(fee))
                min_target_price = ((spend + fee) / bot_trades[len(bot_trades)-1]['amount']) * -1
                print('Price No Profit: ' + str(min_target_price))
                target_price = (min_target_price + min_target_price * config.getfloat('auto_trade', 'price_change')) * -1
                print('Price For Profit: ' + str(target_price))
                est_outcome = spend / target_price
                print('Outcome: ' + str(est_outcome))

                order = post_order('sell', 'limit', est_outcome, target_price * -1, est_outcome * target_price * -1)
                bot_trades.append({
                    'trade': bot_trades[len(bot_trades)-1]['trade']+1,
                    'id': order['id'],
                    'timestamp': time.time(),
                    'exchangetime': order['datetime'],
                    'status': order['status'],
                    'type': order['type'],
                    'side': order['side'],
                    'symbol': order['symbol'],
                    'price': order['price'],
                    'amount': order['amount'],
                    'cost': 0.00,
                    'fee': 0.00,
                    'yield': 0.00,
                    'cumulative_profit': 0.00
                })
                bot_trade_complete_data(bot_trades[len(bot_trades)-1])
                wait_for_order_to_complete()


    except KeyboardInterrupt:
        pass

    input('Debugging Break! Press Any Key To Continue...')



    print('***')
    print(dump(bot_trades))


    input('Press Any Key To Continue...')
    with open('logs/bot-trades_' + time.strftime('%d-%m-%Y_%H-%M-%S', time.localtime(time.time())) + '.log', 'w') as file:
        file.write(dump(bot_trades))



def manual_trade():
    candy.cli_header(secrets.ex, symbol, simulation_pretty, data_fetch_time)

    print('Setting Up A Manual Trade\n')
    print('Current Prices:')
    print(str(ticker['bid']) + ' Bid / ' + str(ticker['ask']) + ' Ask' + '\n')
    print('Current Wallet Balances:')
    print(str(wallets['free'][symbol_single[0]]) + ' ' + symbol_single[0] + ' (used ' + str(wallets['used'][symbol_single[0]]) + ')')
    print(str(wallets['free'][symbol_single[1]]) + ' ' + symbol_single[1] + ' (used ' + str(wallets['used'][symbol_single[1]]) + ')' + '\n')

    # Manual Trade Menu
    def setup_manual_trade():
        print('===================================\n')
        print('[1] Buy ' + symbol_single[0])
        print('[2] Sell ' + symbol_single[0])
        print('-----------------------------------')
        print('[Q] Back To Main Menu\n')

        manual_trade_opt = input('Select An Option: ')

        # Manual Buy TODO into sep func! reuse for initial trade in autotrader
        if manual_trade_opt == '1':
            min_buy = market['limits']['amount']['min'] * ticker['ask']
            print('\nMinimum Buy Is: ' + str(min_buy) + ' ' + symbol_single[1])

            if wallets['free'][symbol_single[1]] < min_buy:
                print('\n> Your ' + symbol_single[1] + ' Balance Is Insufficient, Try Selling ' + symbol_single[0] + '! \n')
                setup_manual_trade()

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
                    post_order('buy', 'market', buy_in/ticker['ask'], ticker['ask'], buy_in)
                elif order_type == '4':
                    desired_price = float(input('At What Price Do You Want To Buy? ' + symbol_single[1] + ': '))
                    post_order('buy', 'limit', buy_in/desired_price, desired_price, buy_in)
                elif order_type == 'Q' or order_type == 'q':
                    return

        # Manual Sell TODO into sep func! reuse for initial trade in autotrader
        elif manual_trade_opt == '2':
            min_sell = market['limits']['amount']['min']
            print('\nMinimum Sell Is: ' + str(min_sell) + ' ' + symbol_single[0])

            if wallets['free'][symbol_single[0]] < min_sell:
                print('\n> Your ' + symbol_single[0] + ' Balance Is Insufficient, Try Buying ' + symbol_single[0] + '! \n')
                setup_manual_trade()

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
                    post_order('sell', 'market', sell_out, ticker['bid'], sell_out*ticker['bid'])
                elif order_type == '4':
                    desired_price = float(input('At What Price Do You Want To Sell? ' + symbol_single[1] + ': '))
                    post_order('sell', 'limit', sell_out, desired_price, sell_out*desired_price)
                elif order_type == 'Q' or order_type == 'q':
                    return


        elif manual_trade_opt == 'Q' or manual_trade_opt == 'q':
            return

        else:
            print('\n> Invalid Answer! Read And Repeat! \n')
            setup_manual_trade()

        # TODO option for another manual trade
        input('\n> Press RETURN To Continue...')
        fetch_all()

    setup_manual_trade()


# Find Crypto Currencies on Exchange that are low minimum buy-in but rather high volume
# Good for debugging
def find_cheap_tradepairs():
    candy.cli_header(secrets.ex, symbol, simulation_pretty, data_fetch_time)

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
def menu():
    candy.cli_header(secrets.ex, symbol, simulation_pretty, data_fetch_time)
    print('[0] Refetch All Data')
    print('[1] Show Summary')
    print('[2] Set Up A Manual Trade')
    print('[3] Start Auto Trading')
    print('[4] Discover Cheap Trade Pairs')
    print('-----------------------------------')
    print('[Q] Quit')
    print('[T] Features In Test\n')

    opt = input('Select An Option: ')
    print('')

    if opt == '0':
        fetch_all()

    elif opt == '1':
        show_summary()
        input('Press RETURN To Continue...')

    elif opt == '2':
        manual_trade()

    elif opt == '3':
        candy.cli_header(secrets.ex, symbol, simulation_pretty, data_fetch_time)
        print('> This Aint Done Yet...')
        input('> Press RETURN To Continue...')

    elif opt == '4':
        find_cheap_tradepairs()
        input('\n> Press RETURN To Continue...')

    elif opt == 'Q' or opt == 'q':
        #os.system('cls' if os.name == 'nt' else 'clear') # todo uncomment for production
        candy.clear()
        sys.exit('You Quit The Program!\nBruv You Gotta Spend Money To Make Money...\n')


    elif opt == 'T' or opt == 't':
        auto_trade()


    else:
        candy.cli_header(secrets.ex, symbol, simulation_pretty, data_fetch_time)
        print('> Invalid Answer! Read And Repeat!')
        input('> Press RETURN To Continue...')


def main():
    candy.cli_header(secrets.ex, symbol, simulation_pretty, data_fetch_time)

    # Check Status Of Exchange & Continue When OK
    exchange_status = exchange.fetch_status()
    log.info('Exchange Status:' + dump(exchange_status))

    if exchange_status['status'] == 'ok':

        candy.welcome_message()
        #fetch_all()

        if args.verbose:
            # Show Features Supported By Exchage
            exchange_features = exchange.has
            log.info('Exchange Features:' + dump(exchange_features))

        if args.verbose:
            # Show Symbol Details / Info
            log.info('Market Info For ' + symbol + ' :' + dump(market))

        while True:
            menu()

    else:
        log.critical('Exchange Status Is Not OK!')


if __name__ == "__main__":
    main()

print('')
print('[ ☑ End Of Program ]')
