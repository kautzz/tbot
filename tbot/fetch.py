"""
tbot fetch.py
Fetching Data From The Exchange. This includes:

*

"""

import ex
import time
import candy
import debug


# Get your last trade from the exchange and drop the info part
def last_trade():
    trades = ex.change.fetch_my_trades(ex.symbol)
    ex.last_trade = trades[len(trades)-1]
    del ex.last_trade['info']


# Get All Open Orders
def open_orders():
    ex.open_orders = ex.change.fetch_open_orders(ex.symbol)
    for list_element in ex.open_orders:
        del list_element['info']


# Update the symbols ticker
def ticker():
    ex.ticker = ex.change.fetch_ticker(ex.symbol)
    del ex.ticker['info']


# Update your wallet balance
def wallet():
    ex.wallets = ex.change.fetch_balance()
    del ex.wallets['info']


# Get Info About The Symbol About To Be Traded
def market():
    ex.markets = ex.change.load_markets()
    ex.market = ex.markets[ex.symbol]


# Get Status Info Of The Exchage
def status():
    ex.status = ex.change.fetch_status()
    debug.log.info('Exchange Status:' + candy.dump(ex.status))
    debug.log.info('Exchange Features:' + candy.dump(ex.change.has))
    return ex.status


# Get All Infos Needed From Exchange
def all():
    ex.data_fetch_time = time.time()
    print('Fetching Data...')
    ticker()
    market()
    last_trade()
    wallet()
    open_orders()
    print('Done!')
