"""
tbot bot.py
Autotrading functions

"""

import ex
import ccxt
import fetch
import trade
import candy
import debug

import time
from configparser import ConfigParser


# Read Config File
config = ConfigParser()
config.read('settings.ini')

def add_bot_order(order):
    """
    The last order executed by any of the bots.

    * Takes response from exchange after placing an order
    * Stores the response into an array
    * Calculates extra metrics for decisionmaking

    """

    order_to_add = [{
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

    order_to_add['cost'] = order_to_add['price'] * order_to_add['amount']

    if order_to_add['type'] == 'limit':
        order_to_add['fee'] = ex.market['maker'] * order_to_add['cost']
    elif order_to_add['type'] == 'market':
        order_to_add['fee'] = ex.market['taker'] * order_to_add['cost']

    if order_to_add['side'] == 'buy':
        order_to_add['yield'] = (order_to_add['cost'] + order_to_add['fee'])
    elif order_to_add['side'] == 'sell':
        order_to_add['yield'] = order_to_add['cost'] - order_to_add['fee']

    # sketchy...
    order_to_add['cumulative_profit'] = bot_trades[len(bot_trades)-2]['cumulative_profit'] + order_to_add['yield']

    ex.bot_orders.append(order_to_add)
    ex.bot_last_order = order_to_add

    debug.log.info('Added To Bot Orders: ' + candy.dump(order_to_add))
    return ex.bot_orders[len(ex.bot_orders)-1]


def order_status(order):
    print("Waiting For " +  + " To Complete ...")
    while True:
        candy.bot_check_order()
        try:
            last_order_status = ex.change.fetch_closed_order(bot_trades[len(bot_trades)-1]['id'])
            if last_order_status['status'] == 'closed':
                bot_trades[len(bot_trades)-1]['status'] = 'closed'
                print('Filled:')
                print(candy.dump(bot_trades[len(bot_trades)-1]))
                break
        except:
            debug.log.info('Could Not Get A Closed Order With ID: ' + str(bot_trades[len(bot_trades)-1]['id']))

        candy.bot_check_order()
        time.sleep(5)

    fetch.ticker()
    candy.clear()



def max_margin_auto_trade():
    """
    Bot For Automatic Trading Of A Maximum Margin

    TODO:

    * Sets up an initial Buy or Sell - MAYBE
    * Creates a limit order for a price change definded in settings - NO
    * Waits until the price hits the target and the order completes - YES
    * Creates a new limit order for the definded price change in the opposite direction - SIMILAR
    * Fees for each trade are automatically calculated and added to target price change - YES
    * Optionally banks a profit percentage on each order as defined in settings - MAYBE
    """

    # You can start this bot with a manual trade if you like
    last_post = trade.manual_trade()
    if last_post:
        add_bot_order(last_post)

    # TODO trade Logic
    ## Buy OR Sell

    print('Press [CONTROL + C] To Stop Trading!')
    try:
        while True:

        ## Peak Detection

        last_bot_post = trade.post_order(side, type, amount, price, cost)
        if last_bot_post:
            add_bot_order(last_bot_post)

    except KeyboardInterrupt:
        pass

    with open('logs/max_margin_bot_trades_' + time.strftime('%d-%m-%Y_%H-%M-%S', time.localtime(time.time())) + '.log', 'w') as file:
        file.write(candy.dump(ex.bot_orders))



    return



def min_margin_auto_trade():
    """
    Bot For Automatic Trading Of A Minimum Margin

    * Sets up an initial Buy or Sell
    * Creates a limit order for a price change definded in settings
    * Waits until the price hits the target and the order completes
    * Creates a new limit order for the definded price change in the opposite direction
    * Fees for each trade are automatically calculated and added to target price change
    * Optionally banks a profit percentage on each order as defined in settings

    Note:

    This works well for currencies that have a regular volatility pattern i.e.
    that usually fluctuate around a specific range. Amplitude and frequency
    of the fluctuation determine how profitable this bot can be. For most
    currencies this bot won't be very efficent as it will not adjust to
    price changes that are continually or out of the ordinary magintude.
    """

    def bot_trade_complete_data(bot_trade):
        bot_trade['cost'] = bot_trade['price'] * bot_trade['amount']

        if bot_trade['type'] == 'limit':
            bot_trade['fee'] = ex.market['maker'] * bot_trade['cost']
        elif bot_trade['type'] == 'market':
            bot_trade['fee'] = ex.market['taker'] * bot_trade['cost']

        if bot_trade['side'] == 'buy':
            bot_trade['yield'] = (bot_trade['cost'] + bot_trade['fee']) * -1
        elif bot_trade['side'] == 'sell':
            bot_trade['yield'] = bot_trade['cost'] - bot_trade['fee']

        bot_trade['cumulative_profit'] = bot_trades[len(bot_trades)-2]['cumulative_profit'] + bot_trade['yield']
        debug.log.info('Last Bot Trade: ' + candy.dump(bot_trade))

    def wait_for_order_to_complete():
        print("Waiting For Last Order To Complete ...")
        while True:
            candy.bot_check_order()
            try:
                last_order_status = ex.change.fetch_closed_order(bot_trades[len(bot_trades)-1]['id'])
                if last_order_status['status'] == 'closed':
                    bot_trades[len(bot_trades)-1]['status'] = 'closed'
                    print('Filled:')
                    print(candy.dump(bot_trades[len(bot_trades)-1]))
                    break
            except:
                debug.log.info('Could Not Get A Closed Order With ID: ' + str(bot_trades[len(bot_trades)-1]['id']))

            candy.bot_check_order()
            time.sleep(5)

        fetch.ticker()
        candy.clear()


    # Decide Whether To Buy Or Sell First
    ## Get last 24h high and low to get the range of price movement
    fetch.ticker()
    range = ex.ticker['high'] - ex.ticker['low']
    print('24h high-low range: ' + str(range))
    print('24h avg price: ' + str(ex.ticker['low'] + range / 2))
    print('current price: ' + str(ex.ticker['close']))
    print('\nSetting Up Initial Trade!')

    if ex.ticker['low'] + range / 2 >= ex.ticker['close']: #todo set to >= for production
        print('Current Price Is On The LOW End Of The 24h Range! Buying First!')
        print('\nCurrent Wallet Balance: ' + str(ex.wallets['free'][ex.symbol_single[1]]) + ' ' + ex.symbol_single[1] + ' (used ' + str(ex.wallets['used'][ex.symbol_single[1]]) + ')')

        min_buy = ex.market['limits']['amount']['min'] * ex.ticker['ask']
        print('Minimum Buy Is: ' + str(min_buy) + ' ' + ex.symbol_single[1])

        if ex.wallets['free'][ex.symbol_single[1]] < min_buy:
            print('\n> Your ' + ex.symbol_single[1] + ' Balance Is Insufficient, Try Selling ' + ex.symbol_single[0] + '! \n')
            input('Press Any Key To Return To Main Menu...')
            return

        buy_in = float(input('How Much Do You Want To Invest? ' + ex.symbol_single[1] + ': '))
        # TODO check for sufficient funds!
        order = trade.post_order('buy', 'market', buy_in/ex.ticker['ask'], ex.ticker['ask'], buy_in)

    else:
        print('Current Price Is On The HIGH End Of The 24h Range! Selling First!')
        print('\nCurrent Wallet Balance: ' + str(ex.wallets['free'][ex.symbol_single[0]]) + ' ' + ex.symbol_single[0] + ' (used ' + str(ex.wallets['used'][ex.symbol_single[0]]) + ')')

        min_sell = ex.market['limits']['amount']['min']
        print('Minimum Sell Is: ' + str(min_sell) + ' ' + ex.symbol_single[0])

        if ex.wallets['free'][ex.symbol_single[0]] < min_sell:
            print('\n> Your ' + ex.symbol_single[0] + ' Balance Is Insufficient, Try Buying ' + ex.symbol_single[0] + '! \n')
            input('Press Any Key To Return To Main Menu...')
            return

        sell_out = float(input('How Much Do You Want To Sell? ' + ex.symbol_single[0] + ': '))
        # TODO check for sufficient funds!
        order = trade.post_order('sell', 'market', sell_out, ex.ticker['bid'], sell_out*ex.ticker['bid'])

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
                candy.bot_buy()

                spend = bot_trades[len(bot_trades)-1]['yield'] - bot_trades[len(bot_trades)-1]['yield'] * config.getfloat('min_margin_auto_trade', 'bank_profit')
                print('Next Investment: ' + str(spend) + ' Banked: ' + str(bot_trades[len(bot_trades)-1]['yield'] * config.getfloat('min_margin_auto_trade', 'bank_profit')))
                fee = ex.market['maker'] * spend
                print('Next Fees: ' + str(fee))
                min_target_price = (spend - fee) / bot_trades[len(bot_trades)-1]['amount']
                print('Price No Profit: ' + str(min_target_price))
                target_price = min_target_price - min_target_price * config.getfloat('min_margin_auto_trade', 'price_change')
                print('Price For Profit: ' + str(target_price))
                est_outcome = spend / target_price
                print('Outcome: ' + str(est_outcome))

                order = trade.post_order('buy', 'limit', spend/target_price, target_price, spend)
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
                candy.bot_sell()

                spend = bot_trades[len(bot_trades)-1]['yield'] - bot_trades[len(bot_trades)-1]['yield'] * config.getfloat('min_margin_auto_trade', 'bank_profit')
                print('Next Investment: ' + str(spend) + ' Banked: ' + str(bot_trades[len(bot_trades)-1]['yield'] * config.getfloat('min_margin_auto_trade', 'bank_profit')))
                fee = ex.market['maker'] * spend * -1
                print('Next Fees: ' + str(fee))
                min_target_price = ((spend + fee) / bot_trades[len(bot_trades)-1]['amount']) * -1
                print('Price No Profit: ' + str(min_target_price))
                target_price = (min_target_price + min_target_price * config.getfloat('min_margin_auto_trade', 'price_change')) * -1
                print('Price For Profit: ' + str(target_price))
                est_outcome = spend / target_price
                print('Outcome: ' + str(est_outcome))

                order = trade.post_order('sell', 'limit', est_outcome, target_price * -1, est_outcome * target_price * -1)
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
    print(candy.dump(bot_trades))


    input('Press Any Key To Continue...')
    with open('logs/min_margin_bot_trades_' + time.strftime('%d-%m-%Y_%H-%M-%S', time.localtime(time.time())) + '.log', 'w') as file:
        file.write(candy.dump(bot_trades))
