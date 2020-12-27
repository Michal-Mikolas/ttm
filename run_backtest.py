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
	sell_modifier=1.00,
	buy_modifier=1.00,
)
storage = ttm.storage.JSONFile('storage.json')  # storage used mainly for strategy
cache = ttm.storage.JSONFile('cache.json')      # storage used only for Bot class
logger = ttm.logger.CSVFile('log.csv', print_to_console=True)

# 7.5k-7.5k: '2018-06-01', '2020-04-24'
# max range: '2018-06-01', '2020-12-26'
bot = ttm.BacktestBot(exchange, strategy, storage, cache, logger, '2018-06-01', '2020-04-24', {
	'BTC': 0.013227,
	'USD': 0.0,
})

#
# Run
#
bot.run()
