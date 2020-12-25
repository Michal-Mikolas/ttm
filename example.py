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

# 10k-.-10k: '2019-09-26', '2020-07-26'
bot = ttm.BacktestBot(exchange, strategy, storage, logger, '2019-09-26', '2020-07-26', {
	'BTC': 0.01,
	'USD': 100,
})

#
# Run
#
bot.run()
