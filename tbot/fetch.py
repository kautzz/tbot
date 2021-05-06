"""
tbot fetch.py
Fetching Data From The Exchange. This includes:

*

"""

import time
import candy




# Get your last trade from the exchange and drop the info part
def last_trade():
    global last_trade
    trades = exchange.fetch_my_trades(symbol)
    last_trade = trades[len(trades)-1]
    del last_trade['info']


# Get All Open Orders
def open_orders():
    global open_orders
    open_orders = exchange.fetch_open_orders(symbol)
    for list_element in open_orders:
	       del list_element['info']


# Update the symbols ticker
def ticker():
    global ticker
    ticker = exchange.fetch_ticker(symbol)
    del ticker['info']


# Update your wallet balance
def wallet():
    global wallets
    wallets = exchange.fetch_balance()
    del wallets['info']


# Get Info About The Symbol About To Be Traded
def market():
    global market
    markets = exchange.load_markets()
    market = markets[symbol]


# Get All Infos Needed From Exchange
def all():
    global data_fetch_time
    data_fetch_time = time.time()
    #candy.cli_header(exchange_name, symbol, simulation_pretty, data_fetch_time)
    print('Fetching Data...')
    ticker()
    market()
    last_trade()
    wallet()
    open_orders()
    print('Done!')
