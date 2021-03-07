import ccxt
import ttm
import keyring
from pprint import pprint

#
# Init
#
data_folder = 'output/universe'

exchange = ttm.exchange.BittrexFix({
    'enableRateLimit': False,
   	'apiKey': keyring.get_password('bittrex', 'apiKey'),
    'secret': keyring.get_password('bittrex', 'secret'),
})
pairs = ttm.Tools.get_pairs(exchange) #; print('# PAIRS:') ; pprint(pairs) ; print(len(pairs))
strategy = ttm.strategy.Universe(
	endpoint='BTC',
	exchange_pairs=pairs,
	executor=ttm.strategy.universe.WorsePriceExecutor(),
	minimal_value=1.00,
	minimal_worse_value=1.00,
	path_length=4,
	tick_period=1,
	limits={'BTC': 0.00060},
)

storage = ttm.storage.JSONFile(data_folder + '/storage-universe.json')  # storage for strategy data
cache = ttm.storage.JSONFile('cache-universe.json')                     # storage for performance optimalisation

logger = ttm.logger.Multi(
	ttm.logger.Console(min_priority=0),
	ttm.logger.CSVFile(data_folder + '/log.csv', min_priority=1),
	ttm.logger.CSVFile(data_folder + '/log-all.csv', min_priority=0),
	# ttm.logger.Gmail(to='nanuqcz@gmail.com', login='nanuqcz@gmail.com', min_priority=2),  # register gmail password to keyring first: https://github.com/kootenpv/yagmail#username-and-password
	# ttm.logger.Telegram(
	# 	token=keyring.get_password('telegram', 'chatbotToken'),        # secures the Telegram bot
	# 	password=keyring.get_password('telegram', 'chatbotPassword'),  # secures the TTM bot
	# 	root_folder=data_folder
	# ),
)
logger.set_pair('BTC/EUR')

bot = ttm.bot.Real(exchange, strategy, storage, cache, logger)

#
# Run
#
bot.run()
