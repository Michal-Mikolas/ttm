import ccxt
import ttm
import keyring

#
# Init
#
data_folder = 'output/ada_eur_keep_value'

exchange = ttm.exchange.BinanceFix({
	'enableRateLimit': True,
	'apiKey': keyring.get_password('binance', 'apiKey'),
    'secret': keyring.get_password('binance', 'secret'),
})
strategy = ttm.strategy.KeepValue(
	pair='ADA/EUR',
	initial_target_value=105.9635,  # EUR
	minimal_move=7.6,               # percent
	tick_period=60,
	timeframe='5m',
	sell_modifier=0.9556842,        # 0.9778421
	buy_modifier=1.0443158,         # 1.0221579
)
storage = ttm.storage.JSONFile(data_folder + '/storage.json')  # storage for strategy data
cache = ttm.storage.JSONFile('cache.json')                     # storage for performance optimalisation

logger = ttm.logger.Multi(
	ttm.logger.Console(min_priority=0),
	ttm.logger.CSVFile(data_folder + '/log-all.csv', min_priority=0),
	ttm.logger.CSVFile(data_folder + '/log.csv', min_priority=1),
	ttm.logger.Gmail(to='nanuqcz@gmail.com', login='nanuqcz@gmail.com', min_priority=2),  # register gmail password to keyring first: https://github.com/kootenpv/yagmail#username-and-password
	ttm.logger.Telegram(
		token=keyring.get_password('telegram', 'adaeurToken'),         # secures the Telegram bot
		password=keyring.get_password('telegram', 'chatbotPassword'),  # secures the TTM bot
		root_folder=data_folder,
	),
)
logger.set_pair('ADA/EUR')

bot = ttm.bot.Real(exchange, strategy, storage, cache, logger)
# bot.set_exceptions_file(data_folder + '/exceptions.log')

#
# Run
#
bot.run()
