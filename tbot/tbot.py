# coding=utf-8
#!/usr/bin/env python3

"""
tbot (WIP)
"""

import os
import sys

import ex
import candy
import fetch
import trade
import bot
import util
import debug


# Are we Running on a Raspberry Pi?
candy.detect_hardware()


# This Shows The Main Menu In The CLI
def menu():
    candy.cli_header()
    candy.menu()
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

    candy.clear()

    if opt == '0':
        fetch.all()

    elif opt == '1':
        util.show_summary()
        input('Press RETURN To Continue...')

    elif opt == '2':
        trade.manual_trade()

    elif opt == '3':
        candy.cli_header()
        print('> This Aint Done Yet...')
        input('> Press RETURN To Continue...')

    elif opt == '4':
        util.find_cheap_tradepairs()
        input('\n> Press RETURN To Continue...')

    elif opt == 'Q' or opt == 'q':
        #os.system('cls' if os.name == 'nt' else 'clear') # todo uncomment for production
        candy.clear()
        sys.exit('You Quit The Program!\nBruv You Gotta Spend Money To Make Money...\n')


    elif opt == 'T' or opt == 't':
        bot.min_margin_auto_trade()


    else:
        candy.cli_header()
        print('> Invalid Answer! Read And Repeat!')
        input('> Press RETURN To Continue...')


def main():
    candy.cli_header()
    ex.login()

    # Check Status Of Exchange & Continue When OK
    exchange_status = fetch.status()
    if exchange_status['status'] == 'ok':

        candy.welcome_message()
        fetch.all()

        while True:
            menu()

    else:
        debug.log.critical('Could Not Connect To Exchange!')


if __name__ == "__main__":
    main()

print('')
print('[ ☑ End Of Program ]')
