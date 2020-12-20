import os
import sys
import time
from datetime import datetime
from dateutil.parser import parse
import ccxt
import ttm

############################################################

# exchange = ccxt.bittrex()

# string = '2019-01-01 00:00:00'
# timestamp = exchange.parse8601(string)
# print(timestamp)
# print(datetime.timestamp(parse(string)))

############################################################

exchange = ccxt.bittrex()

bot = ttm.Bot(exchange, None)
ohlcvs = bot.get_ohlcvs('BTC/USD', '1h', '2019-01-01 09:00:00', '2019-01-01 10:10:00')

for ohlcv in ohlcvs:
	print("%s: %d-%d-%d-%d" % (
		exchange.iso8601(ohlcv[0]),
		ohlcv[1],
		ohlcv[2],
		ohlcv[3],
		ohlcv[4],
	))
print(exchange.milliseconds(), 'Fetched', len(ohlcvs), 'candles')

############################################################

# exchange = ccxt.bittrex()

# from_datetime = '2019-01-01 09:00:00'
# till_datetime = '2019-01-01 09:10:00'
# from_timestamp = exchange.parse8601(from_datetime)
# till_timestamp = exchange.parse8601(till_datetime)

# ohlcvs = exchange.fetch_ohlcv('BTC/EUR', '1h', from_timestamp, till_timestamp)
# for ohlcv in ohlcvs:
# 	print("%s: %d-%d-%d-%d" % (
# 		exchange.iso8601(ohlcv[0]),
# 		ohlcv[1],
# 		ohlcv[2],
# 		ohlcv[3],
# 		ohlcv[4],
# 	))
# print(exchange.milliseconds(), 'Fetched', len(ohlcvs), 'candles')

############################################################

# while True:
# 	orderbook = exchange.fetch_order_book('BTC/EUR')
# 	print(orderbook['bids'][0], orderbook['asks'][0])
# 	time.sleep(2)
