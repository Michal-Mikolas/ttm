import os
import ccxt
import ttm

data_folder = 'output/7.5k-7.5k_1.00-1.00'

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
exchange = ccxt.binance({'enableRateLimit': True})
strategy = ttm.strategy.DCA(
	pair='BTC/USDT',
	initial_target_value=100,  # USD
	minimal_move=5.1,          # percent
	tick_period=5*60,
	timeframe='5m',
	sell_modifier=1.00,  #0.9778421,
	buy_modifier=1.00,  #1.0221579,
)
storage = ttm.storage.JSONFile(data_folder + '/storage.json')  # storage for strategy data
cache = ttm.storage.JSONFile('cache.json')                     # storage for performance optimalisation

logger = ttm.logger.Multi(
	ttm.logger.Console(min_priority=1),
	ttm.logger.CSVFile(data_folder + '/log.csv', min_priority=1),
	ttm.logger.Statistics(storage, data_folder, min_priority=0, export_results={
		'file': 'output/results.csv',
		'note': 'minimal_move=5.1, sell_modifier=1.0, buy_modifier=1.0, initial_target_value=100, pair=BTC/USDT, tick_period=5*60, timeframe=5m',
	}),
	# ttm.logger.Gmail(to='nanuqcz@gmail.com', login='nanuqcz@gmail.com', min_priority=2),  # register gmail password to keyring first: https://github.com/kootenpv/yagmail#username-and-password
)
logger.set_pair('BTC/USDT')

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
