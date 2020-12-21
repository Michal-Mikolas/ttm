import cctx
import ttm

exchange = ccxt.bittrex({
	'enableRateLimit': True,
	'apiKey': 'YOUR_API_KEY',
	'secret': 'YOUR_API_SECRET',
})
strategy = ttm.strategy.SameValue()
storage = ttm.storage.JSON('storage.json')

bot = ttm.Bot(exchange, strategy, storage)
bot.run_backtest('2019-03-01', '2019-04-01')
