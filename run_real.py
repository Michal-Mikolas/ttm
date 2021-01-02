import ccxt
import ttm
import keyring

#
# Init
#
exchange = ccxt.bittrex({
	'enableRateLimit': True,
	'apiKey': keyring.get_password('bittrex', 'apiKey'),
    'secret': keyring.get_password('bittrex', 'secret'),
})
strategy = ttm.strategy.SameValue(
	pair='BTC/EUR',
	initial_target_value=100,  # USD
	minimal_move=5.0,          # percent
	tick_period=60,
	timeframe='5m',
	sell_modifier=0.97,
	buy_modifier=1.03,
)
storage = ttm.storage.JSONFile('real-storage.json')  # storage used mainly for strategy
cache = ttm.storage.JSONFile('cache.json')           # storage used only for Bot class

logger = ttm.logger.Multi(
	ttm.logger.Console(),
	ttm.logger.CSVFile('real-log.csv'),
	ttm.logger.Gmail(to='nanuqcz@gmail.com', login='nanuqcz@gmail.com'),  # register gmail password to keyring first: https://github.com/kootenpv/yagmail#username-and-password
)
logger.set_pair('BTC/USD')

bot = ttm.bot.Real(exchange, strategy, storage, cache, logger)

#
# Run
#
bot.run()
