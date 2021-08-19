import ccxt
import ttm
import keyring

#
# Init
#
data_folder = 'output/neo_usdt_keep_value'

exchange = ccxt.binance({
	'enableRateLimit': True,
	'apiKey': keyring.get_password('binance', 'apiKey'),
    'secret': keyring.get_password('binance', 'secret'),
})
strategy = ttm.strategy.KeepValue(
	pair='NEO/USDT',
	initial_target_value=100.0,  # USDT
	minimal_move=11.6,           # percent
	tick_period=60,
	timeframe='5m',
	sell_modifier=0.9778421,
	buy_modifier=1.0221579,
)
storage = ttm.storage.JSONFile(data_folder + '/storage.json')  # storage for strategy data
cache = ttm.storage.JSONFile('cache.json')                     # storage for performance optimalisation

logger = ttm.logger.Multi(
	ttm.logger.Console(min_priority=0),
	ttm.logger.CSVFile(data_folder + '/log-all.csv', min_priority=0),
	ttm.logger.CSVFile(data_folder + '/log.csv', min_priority=1),
	ttm.logger.Gmail(to='nanuqcz@gmail.com', login='nanuqcz@gmail.com', min_priority=2),  # register gmail password to keyring first: https://github.com/kootenpv/yagmail#username-and-password
	ttm.logger.Telegram(
		token=keyring.get_password('telegram', 'neousdtToken'),        # secures the Telegram bot
		password=keyring.get_password('telegram', 'chatbotPassword'),  # secures the TTM bot
		root_folder=data_folder,
	),
)
logger.set_pair('NEO/USDT')

bot = ttm.bot.Real(exchange, strategy, storage, cache, logger)
# bot.set_exceptions_file(data_folder + '/exceptions.log')

#
# Run
#
bot.run()
