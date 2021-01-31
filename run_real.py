import ccxt
import ttm
import keyring

#
# Init
#
data_folder = 'output/real'

exchange = ccxt.bittrex({
	'enableRateLimit': True,
	'apiKey': keyring.get_password('bittrex', 'apiKey'),
    'secret': keyring.get_password('bittrex', 'secret'),
})
strategy = ttm.strategy.SameValue(
	pair='BTC/EUR',
	initial_target_value=100,  # EUR
	minimal_move=5.0,          # percent
	tick_period=60,
	timeframe='5m',
	sell_modifier=0.97,
	buy_modifier=1.03,
)
storage = ttm.storage.JSONFile(data_folder + '/storage.json')  # storage for strategy data
cache = ttm.storage.JSONFile('cache.json')                     # storage for performance optimalisation

logger = ttm.logger.Multi(
	ttm.logger.Console(min_priority=0),
	ttm.logger.CSVFile(data_folder + '/log.csv', min_priority=1),
	ttm.logger.CSVFile(data_folder + '/log-all.csv', min_priority=0),
	ttm.logger.CSVFile('C:/Users/mikolas/Google Drive/sync/ttm-log.csv', min_priority=0),
	ttm.logger.Gmail(to='nanuqcz@gmail.com', login='nanuqcz@gmail.com', min_priority=2),  # register gmail password to keyring first: https://github.com/kootenpv/yagmail#username-and-password
)
logger.set_pair('BTC/EUR')

bot = ttm.bot.Real(exchange, strategy, storage, cache, logger)

bot.set_chatbot(
	ttm.chatbot.Telegram(
		token=keyring.get_password('telegram', 'chatbotToken'),        # secures the Telegram bot
		password=keyring.get_password('telegram', 'chatbotPassword'),  # secures the trading bot
		root_folder=data_folder
	)
)

#
# Run
#
bot.run()
