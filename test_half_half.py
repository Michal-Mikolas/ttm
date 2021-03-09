import os
import ccxt
import ttm

data_folder = 'output/test_half_half'

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
for mm in range(1, 200):
	mm = mm / 10

	strategy = ttm.strategy.HalfHalf(
		pair         = 'FTM/USDT',
		minimal_move = mm,          # percent
		tick_period  = 60*60,
		timeframe    = '1h',
	)
	storage = ttm.storage.JSONFile(data_folder + '/storage.json')  # storage for strategy data
	cache = ttm.storage.JSONFile('cache.json')                     # storage for performance optimalisation

	logger = ttm.logger.Multi(
		ttm.logger.Console(min_priority=2),
		ttm.logger.CSVFile(data_folder + '/log.csv', min_priority=1),
		ttm.logger.Statistics(storage, data_folder, min_priority=0, export_results={
			'file': 'output/results.csv',
			'note': 'pair=FTM/USDT, minimal_move=%f, tick_period=60*60, timeframe=1h' % (mm),
		}),
		# ttm.logger.Gmail(to='nanuqcz@gmail.com', login='nanuqcz@gmail.com', min_priority=2),  # register gmail password to keyring first: https://github.com/kootenpv/yagmail#username-and-password
	)
	logger.set_pair('FTM/USDT')

	# 0.03-0.03:  '2019-07-04', '2020-08-19'
	bot = ttm.bot.Backtest(exchange, strategy, storage, cache, logger, '2019-07-04', '2020-08-19', {
		'FTM': 0.0,
		'USDT': 100.0,
	})

	#
	# Run
	#
	bot.run()
