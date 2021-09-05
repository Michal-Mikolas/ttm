import os
import ccxt
import ttm

data_folder = 'output/test_keep_value'

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
exchange = ttm.exchange.BinanceFix({'enableRateLimit': True})
for mm in range(40, 202, 2):  # 4-20 % +0.2
	mm = mm / 10

	strategy = ttm.strategy.KeepValue(
		pair='IOTA/USDT',
		initial_target_value=100,  # USD
		minimal_move=mm,           # percent
		tick_period=60*60,
		timeframe='1h',
		sell_modifier=1.00,        # 0.9778421,
		buy_modifier=1.00,         # 1.0221579,
	)
	storage = ttm.storage.JSONFile(data_folder + '/storage.json')  # storage for strategy data
	cache = ttm.storage.JSONFile('cache.json')                     # storage for performance optimalisation

	logger = ttm.logger.Multi(
		ttm.logger.Console(min_priority=1),
		ttm.logger.CSVFile(data_folder + '/log.csv', min_priority=1),
		ttm.logger.Statistics(storage, data_folder, min_priority=0, export_results={
			'file': 'output/results.csv',
			'note': 'minimal_move={:2.1f}, sell_modifier=1.0, buy_modifier=1.0, initial_target_value=0, pair=IOTA/USDT, tick_period=60*60, timeframe=1h'.format(
				mm
			),
		}),
		# ttm.logger.Gmail(to='nanuqcz@gmail.com', login='nanuqcz@gmail.com', min_priority=2),  # register gmail password to keyring first: https://github.com/kootenpv/yagmail#username-and-password
	)
	logger.set_pair('IOTA/USDT')

	# BTCUSDT:  7.5k-7.5k:     '2018-06-01', '2020-04-24'
	# DOGEUSDT: 3.81m-3.83m:   '2019-07-06', '2020-12-19'
	# ETHUSDT:  370-366:       '2018-04-07', '2020-08-17'
	# ETHUSDT:  350-353:       '2017-08-28', '2020-10-05'
	# XRPUSDT:  0.47-0.47:     '2019-06-23', '2021-03-19'
	# XRPUSDT:  0.66-0.64:     '2018-06-10', '2021-04-05'
	# XRPUSDT:  1.66-1.65:     '2018-01-16', '2021-05-02'
	# ADAUSDT:  0.0854-0.0894: '2019-04-03', '2020-09-20'
	# BNBUSDT:  16.10-16.51:   '2020-04-30', '2020-09-06'
	# FTMUSDT:  0.0155-0.0152: '2019-08-15', '2020-11-04'
	# NANOUSDT: 1.70-1.71:     '2019-05-15', '2021-01-04'
	# NANOUSDT: 4.62-4.64:     '2021-02-10', '2021-06-24'
	# LINKUSDT: 14.09-13.74:   '2020-11-21', '2021-07-21'
	# NEOUSDT:  28.2-27.4:     '2018-06-18', '2021-02-09'
	# IOTAUSDT: 0.616-4.625:   '2018-08-09', '2021-06-20'
	#
	# ADABNB:
	# IOTABNB:
	# FTMBNB:   1.3m-1.3m:   '2019-06-19', '2021-05-02'
	bot = ttm.bot.Backtest(exchange, strategy, storage, cache, logger, '2018-08-09', '2021-06-20', {
		'IOTA': 0.0,
		'USDT': 0.0,
	})

	#
	# Run
	#
	bot.run()
