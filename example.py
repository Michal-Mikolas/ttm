import ccxt
import ttm

#
# Clean from last run
#
with open('storage.json', 'w') as file:
	pass
with open('log.csv', 'w') as file:
	pass

#
# Init
#
exchange = ccxt.bittrex()
strategy = ttm.strategy.SameValue(
	pair='BTC/USD',
	minimal_move=5,
	tick_period=60*60,
	timeframe='1h'
)
storage = ttm.storage.JSONFile('storage.json')
logger = ttm.logger.CSVFile('log.csv', print_to_console=True)

# 19k-_4k: '2017-12-17', '2018-12-16'
# 11k-_4k: '2019-08-12', '2020-03-13'
# 10k-_4k: '2019-07-27', '2020-03-13'
# 10k-_-10k: '2019-09-26', '2020-07-27'
bot = ttm.BacktestBot(exchange, strategy, storage, logger, '2019-09-26', '2020-07-27', {
	'BTC': 0.01,
	'USD': 100,
})

#
# Run
#
bot.run()
