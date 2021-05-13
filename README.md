# tbot

### Crypto Currency Exchange CLI & Trading Bot

Using the [CCXT API](https://github.com/ccxt/ccxt) this software connects to your favourite crypto currency exchange and offers a CLI for setting up manual trades for a crypto currency of your choice. Currently it supports placing market and limit orders.

A utility function lets you find volatile crypto currencies with a cheap minimum buyin that may be used for automated trading. Automated trading is still in development and should be considered a proof of concept only.

The software also offers support for running on a RaspberryPi especially in combination with the [Blinkt!](https://github.com/pimoroni/blinkt) LED module and / or the [Adafruit PiOLED](https://github.com/adafruit/Adafruit_CircuitPython_SSD1306) display for pretty eye-candy.

---

Add `secrets.py` to the root folder and add details for your exchange:

```
"""
secrets.py
Credentials for your favourite cryptocurrency exchange.
"""

ex = "your_favourite_exchange"
apiKey = "your_exchange_api_key"
apiSec = "your_exchange_api_secret"
```

 See [CCXT Exchanges](https://github.com/ccxt/ccxt#certified-cryptocurrency-exchanges) for more details. <br /><br />

Check the `settings.ini` file to configure the software.

* `symbol = DOGE/USD` is the currency pair you would like to trade
* `simulation = false` when true will not place any real orders on your exchange <br /><br />

Run with `python -m tbot` use `python -m tbot -v` for verbose output.

---

**General Trading Advice:**

> Do Not Spend Money You Can't Afford To Lose!

> Use At Your Own Risk!
