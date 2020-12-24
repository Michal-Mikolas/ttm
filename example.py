import ccxt
import ttm

exchange = ccxt.bittrex({
	# 'enableRateLimit': True,
	# 'apiKey': '',
	# 'secret': '',
})
strategy = ttm.strategy.SameValue()
storage = ttm.storage.JSONFile('storage.json')

bot = ttm.BacktestBot(exchange, strategy, storage, '2019-01-01', '2019-02-01', {
	'BTC': 0.01,
	'USD': 100,
})
bot.run()
