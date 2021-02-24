import ccxt
import ttm
from datetime import datetime
from pprint import pprint

#
# Init
#
data_folder = 'output/find_universe'

exchanges = ['aax', 'acx', 'aofex', 'bequant', 'bibox', 'bigone', 'binance', 'binanceus',
	'bit2c', 'bitbank', 'bitbay', 'bitcoincom', 'bitfinex', 'bitfinex2', 'bitflyer',
	'bitforex', 'bitget', 'bithumb', 'bitkk', 'bitmart', 'bitmax', 'bitmex', 'bitpanda',
	'bitso', 'bitstamp', 'bitstamp1', 'bittrex', 'bitvavo', 'bitz', 'bl3p', 'bleutrade',
	'braziliex', 'btcalpha', 'btcbox', 'btcmarkets', 'btctradeua', 'btcturk', 'buda',
	'bw', 'bybit', 'bytetrade', 'cdax', 'cex', 'chilebit', 'coinbase', 'coinbaseprime',
	'coinbasepro', 'coincheck', 'coinegg', 'coinex', 'coinfalcon', 'coinfloor', 'coingi',
	'coinmarketcap', 'coinmate', 'coinone', 'coinspot', 'crex24', 'currencycom', 'delta',
	'deribit', 'digifinex', 'dsx', 'eterbase', 'exmo', 'exx', 'fcoin', 'fcoinjp',
	'flowbtc', 'foxbit', 'ftx', 'gateio', 'gemini', 'gopax', 'hbtc', 'hitbtc', 'hollaex',
	'huobijp', 'huobipro', 'ice3x', 'idex', 'independentreserve', 'indodax', 'itbit',
	'kraken', 'kucoin', 'kuna', 'lakebtc', 'latoken', 'lbank', 'liquid', 'luno', 'lykke',
	'mercado', 'mixcoins', 'novadax', 'oceanex', 'okcoin', 'okex', 'paymium', 'phemex',
	'poloniex', 'probit', 'qtrade', 'rightbtc', 'ripio', 'southxchange', 'stex',
	'surbitcoin', 'therock', 'tidebit', 'tidex', 'timex', 'upbit', 'vaultoro', 'vbtc',
	'vcc', 'wavesexchange', 'whitebit', 'xbtce', 'xena', 'yobit', 'zaif', 'zb']
exchanges = ['timex', 'therock', 'southxchange', 'exx', 'hitbtc', 'huobijp', 'bittrex',
	'oceanex', 'kucoin', 'bitvavo', 'liquid', 'binanceus', 'cex', 'bitfinex', 'bigone',
	'coinex', 'aax', 'acx', 'aofex', 'bequant', 'binance', 'bitcoincom', 'bitfinex2',
	'bitget', 'bithumb', 'bitmart', 'bitmex', 'bitpanda', 'braziliex', 'bybit',
	'bytetrade', 'cdax', 'coinfalcon', 'currencycom', 'delta', 'deribit', 'eterbase',
	'exmo', 'ftx', 'gopax', 'hbtc', 'hollaex', 'huobipro', 'ice3x', 'kuna', 'lbank',
	'novadax', 'okcoin', 'okex', 'rightbtc', 'tidebit', 'vcc', 'xena']
exchanges = ['timex', 'therock', 'southxchange', 'exx', 'hitbtc', 'huobijp', 'bittrex',
	'oceanex', 'kucoin', 'bitvavo', 'liquid', 'binanceus', 'cex', 'bitfinex', 'bigone',
	'coinex', 'aax', 'acx']
'''
TOP:
'''

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
	for exchange_name in exchanges:
		for i in range(5):
			# try:
			print(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '  ' + exchange_name)

			#
			# 1) Prepare everything
			#
			exchange = ttm.Tools.get_class('ccxt.' + exchange_name)({
				'enableRateLimit': True,
			})

			if not exchange.has['createMarketOrder'] or not exchange.has['createMarketOrder']:
				raise Exception("%s doesn't support market orders." % exchange_name)

			pairs = ttm.Tools.get_pairs(exchange) #; print('# PAIRS:') ; pprint(pairs) ; print(len(pairs))
			endpoint = ttm.Tools.find_popular_base(pairs)

			bot = ttm.bot.Real(
				exchange,
				ttm.strategy.Universe(
					exchange_pairs=pairs,
					target=endpoint,
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
				path_length=4,
				min_value_after_fees=1.01,
				min_bids_count=12,
				min_asks_count=12,
			)

			# Save results into statistics
			# - init stats
			all_stats = storage.get('all_stats') or {}
			if exchange_name not in all_stats:
				all_stats[exchange_name] = {
					'rounds': 0,
					'value': 100,
					'pairs_count': len(pairs),
					'paths_count': 0,
					'paths': {},
				}

			# - count stats
			all_stats[exchange_name]['rounds'] += 1
			for path_key, path_info in paths.items():
				print(" • %s: %f" % (path_key, path_info['value']))
				all_stats[exchange_name]['value'] *= path_info['value']

				if path_key not in all_stats[exchange_name]['paths']:
					all_stats[exchange_name]['paths'][path_key] = {
						'rounds': 0,
						'value': 100,
						'value_fee_free': 100,
						'datetime': [],
						'last_value': 100,
						'last_value_fee_free': 100,
						'last_fees': 0.0,
						'steps': [],
						'order_books': {},
					}

				all_stats[exchange_name]['paths'][path_key]['rounds'] += 1
				all_stats[exchange_name]['paths'][path_key]['value'] *= path_info['value']
				all_stats[exchange_name]['paths'][path_key]['value_fee_free'] *= path_info['value_fee_free']
				all_stats[exchange_name]['paths'][path_key]['datetime'].append(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
				all_stats[exchange_name]['paths'][path_key]['last_value'] = path_info['value']
				all_stats[exchange_name]['paths'][path_key]['last_value_fee_free'] = path_info['value_fee_free']
				all_stats[exchange_name]['paths'][path_key]['last_fees'] = path_info['value_fee_free'] - path_info['value']
				all_stats[exchange_name]['paths'][path_key]['steps'] = path_info['steps']
				all_stats[exchange_name]['paths'][path_key]['order_books'] = path_info['order_books']

			all_stats[exchange_name]['paths_count'] = len(all_stats[exchange_name]['paths'])

			# - save stats
			all_stats = {k:all_stats[k] for k in sorted(all_stats, key=lambda k: all_stats[k]['value'], reverse=True)}
			storage.save('all_stats', all_stats)

			# except Exception as e:
			# 	exceptions = storage.get('exceptions') or {}
			# 	if exchange_name not in exceptions:
			# 		exceptions[exchange_name] = []

			# 	exceptions[exchange_name] = type(e).__name__ + ': ' + str(e)[0:255]
			# 	storage.save('exceptions', exceptions)
