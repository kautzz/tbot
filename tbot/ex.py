"""
tbot ex.py
Global Exchange Data and Variables

"""

import ccxt
import secrets
import time
from configparser import ConfigParser

# Read Config File
config = ConfigParser()
config.read('settings.ini')

change_name = secrets.ex
symbol = config.get('main', 'symbol')
symbol_single = symbol.split('/', 1)

simulation = config.getboolean('main', 'simulation')
if simulation == True:
    simulation_pretty = 'SIM'
else:
    simulation_pretty = 'HOT'

global status
global market
global ticker
global wallets
global last_trade
global open_orders
global data_fetch_time
data_fetch_time = time.time()

# Log In To Exchange
def login():
    print('Connecting To Crypto Exchange...')
    exchange_class = getattr(ccxt, secrets.ex)
    global change
    change = exchange_class({
        'apiKey': secrets.apiKey,
        'secret': secrets.apiSec,
        'timeout': 30000,
        'enableRateLimit': True,
    })
