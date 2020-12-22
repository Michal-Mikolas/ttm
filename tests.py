import os
import sys
import time
from datetime import datetime
from dateutil.parser import parse
import ccxt
import ttm

exchange = ccxt.bittrex()
strategy = ttm.strategy.SameValue()
storage = ttm.storage.JSONFile('storage.txt')
bot = ttm.BacktestBot(exchange, strategy, storage, '2019-01-01', '2019-02-01')

############################################################

storage.save('a', 'AAA')
storage.save('b', u'Žluťoučký kůň úpěl ďábelské ódy.')
storage.save('c', 'CCC')
assert storage.get('b') == u'Žluťoučký kůň úpěl ďábelské ódy.', "Storage unicode string test failed"
assert storage.get('_nonexisting key') == None, "Storage 'None' test failed"

############################################################

string = '2019-01-01 00:00:00'
timestamp1 = exchange.parse8601(string)
timestamp2 = bot._to_exchange_timestamp(parse(string))
assert timestamp1 == timestamp2, "Datetime to timestamp conversion failed"

############################################################

ohlcvs = bot.get_ohlcvs('BTC/USD', '1h', '2019-01-01 09:00:00', '2019-01-01 10:10:00')
assert len(ohlcvs) == 2, "bot.get_ohlcvs() test failed"
assert int(ohlcvs[0][1]) == 3715, "bot.get_ohlcvs() test 2 failed"
assert int(ohlcvs[1][4]) == 3704, "bot.get_ohlcvs() test 3 failed"

# TODO should return only first day
ohlcvs = bot.get_ohlcvs('BTC/USD', '1h')
for ohlcv in ohlcvs:
	print("%s: %d-%d-%d-%d" % (exchange.iso8601(ohlcv[0]), ohlcv[1], ohlcv[2], ohlcv[3], ohlcv[4]))
print(exchange.milliseconds(), 'Fetched', len(ohlcvs), 'candles')
assert len(ohlcvs) == 744, "bot.get_ohlcvs() test 4 failed"
assert int(ohlcvs[743][1]) == 3419, "bot.get_ohlcvs() test 5 failed"

# TODO pagination
ohlcvs = bot.get_ohlcvs('BTC/USD', '1h', '2019-01-01 09:00:00', '2019-04-01 10:10:00')
print(exchange.milliseconds(), 'Fetched', len(ohlcvs), 'candles')
# assert len(ohlcvs) == ~2200, "bot.get_ohlcvs() pagination test failed"

############################################################

# while True:
# 	orderbook = exchange.fetch_order_book('BTC/EUR')
# 	print(orderbook['bids'][0], orderbook['asks'][0])
# 	time.sleep(2)

print("")
print("All test passed :-)")
