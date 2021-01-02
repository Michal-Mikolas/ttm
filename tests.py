from datetime import datetime
from dateutil.parser import parse
import ccxt
import ttm

exchange = ccxt.bittrex({'enableRateLimit': True})
strategy = ttm.strategy.SameValue()
storage = ttm.storage.JSONFile('storage.json')
bot = ttm.bot.Backtest(exchange, strategy, storage, '2019-01-01', '2019-04-01')

#
# Fee
#
fee = bot._calculate_fee('BTC/USD', 'limit', 'buy', 0.01, 10000)
assert fee['cost'] == 0.25, "'Calculate fee' test failed"

#
# Storage
#
storage.save('a', 'AAA')
storage.save('b', u'Žluťoučký kůň úpěl ďábelské ódy.')
storage.save('c', 'CCC')
assert storage.get('b') == u'Žluťoučký kůň úpěl ďábelské ódy.', "Storage unicode string test failed"
assert storage.get('_nonexisting key') == None, "Storage 'None' test failed"

#
# Exchange timestamps
#
string = '2019-01-01 00:00:00'
timestamp1 = exchange.parse8601(string)
timestamp2 = bot._to_exchange_timestamp(parse(string))
assert timestamp1 == timestamp2, "Datetime to timestamp conversion failed"

#
# Get OHLCVs
#
ohlcvs = bot.get_ohlcvs('BTC/USD', '1h', '2019-01-01 09:00:00', '2019-01-01 10:10:00')
first = datetime.utcfromtimestamp(ohlcvs[0][0] / 1000)
last = datetime.utcfromtimestamp(ohlcvs[-1][0] / 1000)
assert first.strftime('%Y-%m-%d %H:%M:%S') == '2019-01-01 09:00:00', "bot.get_ohlcvs() basic test failed"
assert last.strftime('%Y-%m-%d %H:%M:%S') == '2019-01-01 10:00:00', "bot.get_ohlcvs() basic test 2 failed"

ohlcvs = bot.get_ohlcvs('BTC/USD', '1h')
last = datetime.utcfromtimestamp(ohlcvs[-1][0] / 1000)
assert last.strftime('%Y-%m-%d') == '2019-03-31', "bot.get_ohlcvs() 'no date interval' test failed"

ohlcvs = bot.get_ohlcvs('BTC/USD', '1h', '2019-01-01 12:00:00', '2019-04-01 12:00:00')
# for ohlcv in ohlcvs:
# 	print("%s: %d-%d-%d-%d" % (exchange.iso8601(ohlcv[0]), ohlcv[1], ohlcv[2], ohlcv[3], ohlcv[4]))
# print(exchange.milliseconds(), 'Fetched', len(ohlcvs), 'candles')
first = datetime.utcfromtimestamp(ohlcvs[0][0] / 1000)
last = datetime.utcfromtimestamp(ohlcvs[-1][0] / 1000)
assert first.strftime('%Y-%m-%d') == '2019-01-01', "bot.get_ohlcvs() pagination test failed"
assert last.strftime('%Y-%m-%d') == '2019-03-31', "bot.get_ohlcvs() pagination test 2 failed"

############################################################
# while True:
# 	orderbook = exchange.fetch_order_book('BTC/EUR')
# 	print(orderbook['bids'][0], orderbook['asks'][0])
# 	time.sleep(2)

print("")
print("All test passed :-)")
