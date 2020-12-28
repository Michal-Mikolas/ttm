import os
import ccxt
import ttm

#
# Clean from last run
#
try:
	os.remove('backtest-storage.json')
	os.remove('backtest-log.csv')
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
	sell_modifier=0.97,
	buy_modifier=1.03,
)
storage = ttm.storage.JSONFile('backtest-storage.json')  # storage used mainly for strategy
cache = ttm.storage.JSONFile('cache.json')               # storage used only for Bot class
logger = ttm.logger.Multi(
	ttm.logger.Console(),
	ttm.logger.CSVFile('backtest-log.csv'),
	# ttm.logger.Gmail(to='nanuqcz@gmail.com', login='nanuqcz@gmail.com'),
)

# max range:  '2018-06-01', '2020-12-26'
# 7.5k-7.5k:  '2018-06-01', '2020-04-24'
# 7.5k-24.5k: '2020-04-24', '2020-12-26'
bot = ttm.BacktestBot(exchange, strategy, storage, cache, logger, '2018-06-01', '2020-04-24', {
	'BTC': 0.013227,
	'USD': 0.0,
})

#
# Run
#
bot.run()
