import os
import sys
import time

import ccxt

exchange = ccxt.bittrex()
while True:
	orderbook = exchange.fetch_order_book('BTC/EUR')
	print(orderbook['bids'][0], orderbook['asks'][0])
	time.sleep(2)
