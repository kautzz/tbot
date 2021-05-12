"""
tbot util.py
Exchange & Trade Utility functions

"""

import ex
import ccxt
import candy
import time

# Show a summary of the most important Details
def show_summary():
    candy.cli_header()
    print('Here Is A Summary Of Your Data:')
    print('Fetched At: ' + time.ctime(ex.data_fetch_time) + '\n')

    wallet_summary = ex.wallets
    del wallet_summary['free']
    del wallet_summary['used']
    del wallet_summary['total']
    print('Your Wallet Balances:' + candy.dump(wallet_summary))

    print('Open Orders: ' + candy.dump(ex.open_orders))

    print('Your Last Trade:' + candy.dump(ex.last_trade))

    market_summary = ex.market
    del market_summary['tiers']
    print('Market Info: ' + candy.dump(market_summary))

    print('Ticker: ' + candy.dump(ex.ticker))


# Find Crypto Currencies on Exchange that are low minimum buy-in but rather high volume
# Good for debugging
def find_cheap_tradepairs():
    candy.cli_header()

    tickers = ex.change.fetch_tickers()
    tickers_tuples = list(ccxt.Exchange.keysort(tickers).items())

    markets = ex.change.load_markets()
    tuples = list(ccxt.Exchange.keysort(markets).items())

    # output a table of all markets
    print('{:<10} {:<7} {:<7} {:<7} {:<10} {:<10} {:<6} {:<13} {:<13}'.format('symbol', 'taker', 'maker', 'limit', 'bid', 'buyin', '%', 'vol', 'vol/buyin'))
    for (k, v) in tuples:
        if v['quote'] == 'USD':
            if round(tickers[v['symbol']]['bid']*v['limits']['amount']['min'],6) <= 0.5:
                if round(tickers[v['symbol']]['baseVolume']) >= 5000:
                    if round(tickers[v['symbol']]['baseVolume']/tickers[v['symbol']]['bid']*v['limits']['amount']['min'],4) >= 50:
                        print('{:<10} {:<7} {:<7} {:<7} {:<10} {:<10} {:<6} {:<13} {:<13}'.format(v['symbol'], v['taker'], v['maker'], v['limits']['amount']['min'], tickers[v['symbol']]['bid'], round(tickers[v['symbol']]['bid']*v['limits']['amount']['min'],6), round(tickers[v['symbol']]['percentage'],3), round(tickers[v['symbol']]['baseVolume'],3), round(tickers[v['symbol']]['baseVolume']/tickers[v['symbol']]['bid']*v['limits']['amount']['min'],4)))
