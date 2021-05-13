"""
tbot trade.py
Trade functions

"""

import ex
import ccxt
import fetch
import candy
import debug
import time

# Create an order to buy or sell Crypto
def post_order(side, type, amount, price, cost):
    print('\n===================================\n')
    print('Posting Order: ' + type + ' ' + side + ' ' + str(amount) + ' ' + ex.symbol_single[0] + ' @ ' + str(price) + ' ' + ex.symbol_single[1])
    print('Total: ' + str(cost) + ' ' + ex.symbol_single[1] + '\n')

    if ex.simulation == False:
        order = ex.change.createOrder(ex.symbol, type, side, amount, price)
        candy.notification_sound()
        debug.log.info('Created Order: ' + candy.dump(order))
        return order

    else:
        print('You Are Running A Simulation! Nothing Happened...')
        return


def manual_trade():
    candy.cli_header()

    print('Setting Up A Manual Trade\n')
    print('Current Prices:')
    print(str(ex.ticker['bid']) + ' Bid / ' + str(ex.ticker['ask']) + ' Ask' + '\n')
    print('Current Wallet Balances:')
    print(str(ex.wallets['free'][ex.symbol_single[0]]) + ' ' + ex.symbol_single[0] + ' (used ' + str(ex.wallets['used'][ex.symbol_single[0]]) + ')')
    print(str(ex.wallets['free'][ex.symbol_single[1]]) + ' ' + ex.symbol_single[1] + ' (used ' + str(ex.wallets['used'][ex.symbol_single[1]]) + ')' + '\n')

    # Manual Trade Menu
    def setup_manual_trade():
        print('===================================\n')
        print('[1] Buy ' + ex.symbol_single[0])
        print('[2] Sell ' + ex.symbol_single[0])
        print('-----------------------------------')
        print('[Q] Back To Main Menu\n')

        manual_trade_opt = input('Select An Option: ')

        # Manual Buy TODO into sep func! reuse for initial trade in autotrader
        if manual_trade_opt == '1':
            min_buy = ex.market['limits']['amount']['min'] * ex.ticker['ask']
            print('\nMinimum Buy Is: ' + str(min_buy) + ' ' + ex.symbol_single[1])

            if ex.wallets['free'][ex.symbol_single[1]] < min_buy:
                print('\n> Your ' + ex.symbol_single[1] + ' Balance Is Insufficient, Try Selling ' + ex.symbol_single[0] + '! \n')
                setup_manual_trade()

            else:
                buy_in = float(input('How Much Do You Want To Invest? ' + ex.symbol_single[1] + ': '))
                # TODO check for sufficient funds!

                print('')
                print('[3] market Order @ ' + str(ex.ticker['ask']))
                print('[4] Limit Order')
                print('-----------------------------------')
                print('[Q] Back To Main Menu\n')
                order_type = input('Select An Option: ')

                if order_type == '3':
                    post_order('buy', 'market', buy_in/ex.ticker['ask'], ex.ticker['ask'], buy_in)
                elif order_type == '4':
                    desired_price = float(input('At What Price Do You Want To Buy? ' + ex.symbol_single[1] + ': '))
                    post_order('buy', 'limit', buy_in/desired_price, desired_price, buy_in)
                elif order_type == 'Q' or order_type == 'q':
                    return

        # Manual Sell TODO into sep func! reuse for initial trade in autotrader
        elif manual_trade_opt == '2':
            min_sell = ex.market['limits']['amount']['min']
            print('\nMinimum Sell Is: ' + str(min_sell) + ' ' + ex.symbol_single[0])

            if ex.wallets['free'][ex.symbol_single[0]] < min_sell:
                print('\n> Your ' + ex.symbol_single[0] + ' Balance Is Insufficient, Try Buying ' + ex.symbol_single[0] + '! \n')
                setup_manual_trade()

            else:
                sell_out = float(input('How Much Do You Want To Sell? ' + ex.symbol_single[0] + ': '))
                # TODO check for sufficient funds!

                print('')
                print('[3] market Order @ ' + str(ex.ticker['bid']))
                print('[4] Limit Order')
                print('-----------------------------------')
                print('[Q] Back To Main Menu\n')
                order_type = input('Select An Option: ')

                if order_type == '3':
                    post_order('sell', 'market', sell_out, ex.ticker['bid'], sell_out*ex.ticker['bid'])
                elif order_type == '4':
                    desired_price = float(input('At What Price Do You Want To Sell? ' + ex.symbol_single[1] + ': '))
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
        fetch.all()

    setup_manual_trade()
