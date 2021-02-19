import ccxt
import ttm
import keyring
from pprint import pprint

#
# Init
#
data_folder = 'output/universe'

# binance,bitmex,okex,bitfinex,zb,acx,aofex,bequant,bibox,bigone,binanceus,
#   bitfinex,bitget,bithumb,bitkk,bitpanda,bitz,bleutrade,braziliex,bw,bybit,
#   cdax,coincheck,coinex,coinfalcon,coinfloor,coingi,coinmarketcap,coinone,
#   coinspot,currencycom,
# bit2c!,bitbank!,bitbay!,bitflyer!,bitforex!,bitmax!,bitso!,bitstamp!,bl3p!,
#   btcalpha!,btcbox!,btcmarkets!,btctradeua!,btcturk!,buda!,bytetrade!,
#   chilebit!,coinbase!,coinbaseprime!,coinbasepro!,coinegg!,coinmate!,crex24!,
# bitvavo,bitmart,coinex,hitbtc,bittrex,cex,
exchange = ccxt.cex({
	'enableRateLimit': True,
})
pairs = ttm.Tools.get_pairs(exchange) ; print('# PAIRS:') ; pprint(pairs) ; print(len(pairs))
strategy = ttm.strategy.Universe(
	exchange_pairs=pairs,
	target=ttm.Tools.find_popular_base(pairs),
	minimal_profit=0.3,  # percent
	path_length=4,
	tick_period=10,
)

storage = ttm.storage.JSONFile(data_folder + '/storage-universe.json')  # storage for strategy data
cache = ttm.storage.JSONFile('cache-universe.json')                     # storage for performance optimalisation

logger = ttm.logger.Multi(
	ttm.logger.Console(min_priority=0),
	ttm.logger.CSVFile(data_folder + '/log.csv', min_priority=1),
	ttm.logger.CSVFile(data_folder + '/log-all.csv', min_priority=0),
	# ttm.logger.CSVFile('C:/Users/mikolas/Google Drive/sync/ttm-log.csv', min_priority=0),
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
