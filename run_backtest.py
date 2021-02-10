import os
import ccxt
import ttm

data_folder = 'output/7.5k-7.5k_0.97-1.03_0.7'

#
# Clean from last run
#
try:
	os.remove(data_folder + '/storage.json')
	os.remove(data_folder + '/log.csv')
except:
	pass

#
# Init
#
exchange = ccxt.bittrex({'enableRateLimit': True})
strategy = ttm.strategy.SameValue(
	pair='BTC/USD',
	initial_target_value=100,  # USD
	minimal_move=5.0,          # percent
	tick_period=60*60,
	timeframe='1h',
	sell_modifier=0.97,
	buy_modifier=1.03,
)
storage = ttm.storage.JSONFile(data_folder + '/storage.json')  # storage for strategy data
cache = ttm.storage.JSONFile('cache.json')                     # storage for performance optimalisation

logger = ttm.logger.Multi(
	ttm.logger.Console(min_priority=1),
	ttm.logger.CSVFile(data_folder + '/log.csv', min_priority=1),
	ttm.logger.Statistics(storage, data_folder, min_priority=0, export_results={
		'file': 'output/results.csv',
		'extra_values': {
			'minimal_move': 5.0,
			'sell_modifier': 1.0,
			'buy_modifier': 1.0,
			# 'strategy': 'SameValue',
			# 'exchange': 'Bittrex',
			# 'from': '2018-06-01',
			# 'till': '2020-04-24',
		},
	}),
	# ttm.logger.Gmail(to='nanuqcz@gmail.com', login='nanuqcz@gmail.com', min_priority=2),  # register gmail password to keyring first: https://github.com/kootenpv/yagmail#username-and-password
)
logger.set_pair('BTC/USD')

# max range:  '2018-06-01', '2020-12-26'
# 7.5k-7.5k:  '2018-06-01', '2020-04-24'
# 7.5k-24.5k: '2020-04-24', '2020-12-26'
bot = ttm.bot.Backtest(exchange, strategy, storage, cache, logger, '2018-06-01', '2020-04-24', {
	'BTC': 0.0,
	'USD': 0.0,
})

#
# Run
#
bot.run()
