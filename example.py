import os
import ccxt
import ttm

#
# Clean from last run
#
try:
	os.remove('storage.json')
	os.remove('log.csv')
except:
	pass

#
# Init
#
exchange = ccxt.bittrex()
strategy = ttm.strategy.SameValue(
	pair='BTC/USD',
	initial_target_value=100,  # USD
	minimal_move=5.0,          # percent
	tick_period=60*60,
	timeframe='1h',
	sell_modifier=0.95,
	buy_modifier=1.00,
)
storage = ttm.storage.JSONFile('storage.json')
logger = ttm.logger.CSVFile('log.csv', print_to_console=True)

# 19k-_4k: '2017-12-17', '2018-12-16'
# 11k-_4k: '2019-08-12', '2020-03-13'
# 10k-_4k: '2019-07-27', '2020-03-13'
# 10k-_-10k: '2019-09-26', '2020-07-27'
# max range: '2018-06-01', '2020-12-26'
bot = ttm.BacktestBot(exchange, strategy, storage, logger, '2018-06-01', '2020-12-26', {
	'BTC': 0.013227,
	'USD': 0.0,
})

#
# Run
#
bot.run()
