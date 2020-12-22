import cctx
import ttm

exchange = ccxt.bittrex({
	'enableRateLimit': True,
	'apiKey': 'YOUR_API_KEY',
	'secret': 'YOUR_API_SECRET',
})
strategy = ttm.strategy.SameValue()
storage = ttm.storage.JSONFile('storage.json')

bot = ttm.BacktestBot(exchange, strategy, storage)
bot.run('2019-03-01', '2019-04-01')
