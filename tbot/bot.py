"""
tbot bot.py
Autotrading functions

"""

import ex
import ccxt
import candy
import time
import debug

#TODO TODO TODO
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
            candy.bot_check_order()
            try:
                last_order_status = exchange.fetch_closed_order(bot_trades[len(bot_trades)-1]['id'])
                if last_order_status['status'] == 'closed':
                    bot_trades[len(bot_trades)-1]['status'] = 'closed'
                    print('Filled:')
                    print(dump(bot_trades[len(bot_trades)-1]))
                    break
            except:
                pass
            candy.bot_check_order()
            time.sleep(5)

        fetch.ticker()
        candy.clear()


    # Decide Whether To Buy Or Sell First
    ## Get last 24h high and low to get the range of price movement
    fetch.ticker()
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
                candy.bot_buy()

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
                candy.bot_sell()

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
