import ccxt
import ttm
from datetime import datetime
from pprint import pprint

#
# Init
#
split = 5
data_folder = 'output/find_universe/%d' % split

# # all
# exchanges = [
# 	'aax', 'aofex', 'ascendex', 'bequant', 'bibox', 'bigone', 'binance', 'binancecoinm', 'binanceus',
# 	'binanceusdm', 'bit2c', 'bitbank', 'bitbay', 'bitbns', 'bitcoincom', 'bitfinex', 'bitfinex2',
# 	'bitflyer', 'bitforex', 'bitget', 'bithumb', 'bitmart', 'bitmex', 'bitpanda', 'bitso', 'bitstamp',
# 	'bitstamp1', 'bittrex', 'bitvavo', 'bitz', 'bl3p', 'braziliex', 'btcalpha', 'btcbox', 'btcmarkets',
# 	'btctradeua', 'btcturk', 'buda', 'bw', 'bybit', 'bytetrade', 'cdax', 'cex', 'coinbase',
# 	'coinbaseprime', 'coinbasepro', 'coincheck', 'coinegg', 'coinex', 'coinfalcon', 'coinfloor',
# 	'coinmarketcap', 'coinmate', 'coinone', 'coinspot', 'crex24', 'currencycom', 'delta', 'deribit',
# 	'digifinex', 'equos', 'exmo', 'exx', 'flowbtc', 'ftx', 'gateio', 'gemini', 'gopax', 'hbtc',
# 	'hitbtc', 'hollaex', 'huobijp', 'huobipro', 'idex', 'independentreserve', 'indodax', 'itbit',
# 	'kraken', 'kucoin', 'kuna', 'latoken', 'lbank', 'liquid', 'luno', 'lykke', 'mercado', 'mixcoins',
# 	'ndax', 'novadax', 'oceanex', 'okcoin', 'okex', 'okex5', 'paymium', 'phemex', 'poloniex', 'probit',
# 	'qtrade', 'rightbtc', 'ripio', 'southxchange', 'stex', 'therock', 'tidebit', 'tidex', 'timex',
# 	'upbit', 'vcc', 'wavesexchange', 'whitebit', 'xena', 'yobit', 'zaif', 'zb',
# ]
# exchanges_split = [
# 	exchanges[0:19],
# 	exchanges[19:38],
# 	exchanges[38:57],
# 	exchanges[57:76],
# 	exchanges[76:95],
# 	exchanges[95:114],
# ]

# supported by PathTraveler & Universe strategy
# (has required features: fetch_tickers, fetch_markets, market orders, ...)
exchanges = [
	'aax', 'aofex', 'bequant', 'binance', 'binanceus', 'bitcoincom', 'bitfinex', 'bitfinex2', 'bitget',
	'bithumb', 'bitmart', 'bitpanda', 'bittrex', 'bitvavo', 'cdax', 'cex', 'coinex', 'coinfalcon',
	'currencycom', 'exmo', 'exx', 'ftx', 'gopax', 'hbtc', 'hitbtc', 'hollaex', 'huobijp', 'huobipro',
	'kucoin', 'lbank', 'liquid', 'novadax', 'oceanex', 'okcoin', 'okex', 'okex5', 'rightbtc',
	'southxchange', 'therock', 'tidebit', 'timex', 'upbit', 'vcc',
]
exchanges_split = [
	exchanges[0:7],
	exchanges[7:14],
	exchanges[14:21],
	exchanges[21:28],
	exchanges[28:35],
	exchanges[35:],
]

# # favorites (with historically found opportunities)
# exchanges = ['huobipro', 'upbit', 'southxchange', 'aofex', 'hbtc', 'bitvavo', 'oceanex', 'bittrex']
# exchanges = ['bitcoincom', 'AOFEX', 'bequant', 'bitpanda', 'OCEANEX', 'okex5', 'UPBIT']
# exchanges = []

# # testing only one
# exchanges = ['southxchange']

''' BLACKLIST
OKEX - no API for new accounts
LATOKEN - precision max 10 satoshi (X.XXXX BTC)  TODO send my 30 USD back
'''

simulation_trade_amounts = {
	'BTC': 0.001,
	'EUR': 42.0,
	'USD': 50.0,
	'USDT': 50.0,
	'USxD': 50.0,
	'AUD': 65.0,
	'AQ': 331.0,
	'QC': 333.0,
    'HKD': 388.0,
	'JPY': 5330.0,
	'UAH': 1398.0,
	'KRW': 50000.0,
}

storage = ttm.storage.JSONFile(data_folder + '/storage-universe.json')  # storage for strategy data
cache = ttm.storage.JSONFile('cache-universe.json')                     # storage for performance optimalisation
logger = ttm.logger.Multi(
	ttm.logger.Console(min_priority=0),
	ttm.logger.CSVFile(data_folder + '/log.csv', min_priority=1),
	ttm.logger.CSVFile(data_folder + '/log-all.csv', min_priority=0),
)
logger.set_pair('BTC/USDT')

# Make 'all_stats' appear first in the file, not 'exceptions'
all_stats = storage.get('all_stats') or {}
storage.save('all_stats', all_stats)

# Never-ending work...
while True:
	for exchange_name in exchanges_split[split]:
		exchange_name = exchange_name.lower()

		for i in range(1):
			try:
				print(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '  ' + exchange_name)

				#
				# 1) Prepare everything
				#
				exchange = ttm.Tools.get_class('ccxt.' + exchange_name)({
					'enableRateLimit': False,
				})

				if not exchange.has['createMarketOrder']:
					raise Exception("%s doesn't support market orders." % exchange_name)

				pairs = ttm.Tools.get_pairs(exchange) #; print('# PAIRS:') ; pprint(pairs) ; print(len(pairs))
				if len(pairs) == 0:
					raise Exception("Exchange '%s' has no pairs for trade." % exchange_name)

				endpoint = ttm.Tools.find_popular_quote(pairs)

				if endpoint not in simulation_trade_amounts:
					raise Exception("No simulation trade amount for '%s' was specified." % endpoint)
				trade_amount = simulation_trade_amounts[endpoint]

				bot = ttm.bot.Real(
					exchange,
					ttm.strategy.Universe(
						exchange_pairs = pairs,
						endpoint = endpoint,
						executor = ttm.strategy.universe.Executor(),
					),
					storage,
					cache,
					logger
				)

				#
				# 2) Scan for current options
				#
				paths = bot.strategy.scanner.full_scan(
					pairs,
					endpoint,
					path_length = 4,
					trade_amount = trade_amount,
					min_result_after_fees = trade_amount * 1.00,
					min_worse_result = trade_amount * 1.00,
					min_bids_count = 3,
					min_asks_count = 3,
				)

				# Save results into statistics
				# - init stats
				all_stats = storage.get('all_stats') or {}
				if exchange_name not in all_stats:
					all_stats[exchange_name] = {
						'rounds': 0,
						'result_coef': 1.0,
						'result_coef_fee_free': 1.0,
						'simulation_result_coef': 1.0,
						'worse_result_coef': 1.0,
						'pairs_count': len(pairs),
						'paths_count': 0,
						'paths': {},
					}

				# - count stats
				all_stats[exchange_name]['rounds'] += 1
				for path_key, path_data in paths.items():
					result_coef = path_data['result_amount'] / trade_amount
					result_coef_fee_free = path_data['result_amount_fee_free'] / trade_amount
					simulation_result_coef = path_data['simulation'][-1]['result_amount'] / path_data['simulation'][0]['result_amount']
					worse_result_coef = path_data['simulation'][-1]['worse_result_amount'] / path_data['simulation'][0]['result_amount']

					print(" • %s: %f" % (path_key, simulation_result_coef))

					all_stats[exchange_name]['result_coef'] *= result_coef
					all_stats[exchange_name]['result_coef_fee_free'] *= result_coef_fee_free
					all_stats[exchange_name]['simulation_result_coef'] *= simulation_result_coef
					all_stats[exchange_name]['worse_result_coef'] *= worse_result_coef

					if path_key not in all_stats[exchange_name]['paths']:
						all_stats[exchange_name]['paths'][path_key] = {
							'rounds': 0,
							'result_coef': 1.0,
							'result_coef_fee_free': 1.0,
							'simulation_result_coef': 1.0,
							'worse_result_coef': 1.0,
							'trade_amount': trade_amount,
							'last_result_amount': None,
							'last_result_amount_fee_free': None,
							'last_fees': 0.0,
							'last_result_coef': None,
							'last_result_coef_fee_free': None,
							'last_simulation_result_coef': None,
							'last_worse_result_coef': None,
							'datetime': [],
							'steps': [],
							'simulation': [],
							'order_books': {},
						}

					all_stats[exchange_name]['paths'][path_key]['rounds'] += 1
					all_stats[exchange_name]['paths'][path_key]['result_coef'] *= result_coef
					all_stats[exchange_name]['paths'][path_key]['result_coef_fee_free'] *= result_coef_fee_free
					all_stats[exchange_name]['paths'][path_key]['simulation_result_coef'] *= simulation_result_coef
					all_stats[exchange_name]['paths'][path_key]['worse_result_coef'] *= worse_result_coef
					all_stats[exchange_name]['paths'][path_key]['datetime'].append(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
					all_stats[exchange_name]['paths'][path_key]['last_result_amount'] = path_data['result_amount']
					all_stats[exchange_name]['paths'][path_key]['last_result_amount_fee_free'] = path_data['result_amount_fee_free']
					all_stats[exchange_name]['paths'][path_key]['last_fees'] = path_data['result_amount_fee_free'] - path_data['result_amount']
					all_stats[exchange_name]['paths'][path_key]['last_result_coef'] = result_coef
					all_stats[exchange_name]['paths'][path_key]['last_result_coef_fee_free'] = result_coef_fee_free
					all_stats[exchange_name]['paths'][path_key]['last_simulation_result_coef'] = simulation_result_coef
					all_stats[exchange_name]['paths'][path_key]['last_worse_result_coef'] = worse_result_coef
					all_stats[exchange_name]['paths'][path_key]['steps'] = path_data['steps']
					all_stats[exchange_name]['paths'][path_key]['simulation'] = path_data['simulation']
					all_stats[exchange_name]['paths'][path_key]['order_books'] = path_data['order_books']

				all_stats[exchange_name]['paths_count'] = len(all_stats[exchange_name]['paths'])

				# - save stats
				all_stats = {k:all_stats[k] for k in sorted(all_stats, key=lambda k: all_stats[k]['simulation_result_coef'], reverse=True)}
				storage.save('all_stats', all_stats)

			except Exception as e:
				exceptions = storage.get('exceptions') or {}
				if exchange_name not in exceptions:
					exceptions[exchange_name] = []

				exception_message = "%s: %s" % (type(e).__name__, str(e)[0:255])
				if exception_message not in exceptions[exchange_name]:
					exceptions[exchange_name].append(exception_message)

				storage.save('exceptions', exceptions)
