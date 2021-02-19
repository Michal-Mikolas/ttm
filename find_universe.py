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
exchanges = ['bitvavo', 'stex', 'liquid', 'gateio', 'southxchange', 'bigone', 'timex',
	'poloniex', 'bitmart', 'bw', 'bittrex', 'bitfinex2', 'coinex', 'oceanex', 'bitfinex',
	'huobijp', 'hitbtc', 'exx', 'okex', 'cex', 'bitkk', 'bequant', 'ftx', 'kucoin']

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

# Work work work...
while True:
	for exchange_name in exchanges:
		try:
			print(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '  ' + exchange_name)

			#
			# 1) Prepare everything
			#
			exchange = ttm.Tools.get_class('ccxt.' + exchange_name)({
				'enableRateLimit': True,
			})

			pairs = ttm.Tools.get_pairs(exchange) #; print('# PAIRS:') ; pprint(pairs) ; print(len(pairs))
			strategy = ttm.strategy.Universe(
				exchange_pairs=pairs,
				target=ttm.Tools.find_popular_base(pairs),
				minimal_profit=0.3,  # percent
				path_length=4,
				tick_period=10,
			)

			bot = ttm.bot.Real(exchange, strategy, storage, cache, logger)

			#
			# 2) Simulate one tick
			#

			# Do the tick
			strategy.start()
			stats = strategy.tick()

			# Save results into statistics
			# TODO stats[path]['fees']
			# TODO stats[path]['last_value']
			# - init stats
			all_stats = storage.get('all_stats') or {}
			if exchange_name not in all_stats:
				all_stats[exchange_name] = {
					'rounds': 0,
					'value': 100,
					'paths': {},
				}

			# - count stats
			all_stats[exchange_name]['rounds'] += 1
			for path_key, path_stats in stats.items():
				all_stats[exchange_name]['value'] *= path_stats['value'] / 100

				if path_key not in all_stats[exchange_name]['paths']:
					all_stats[exchange_name]['paths'][path_key] = {
						'rounds': 0,
						'value': 100,
						'value_fee_free': 100,
						'fees': 0.0,
						'last_value': 100,
						'last_value_fee_free': 100,
						'last_fees': 0.0,
					}

				all_stats[exchange_name]['paths'][path_key]['rounds'] += 1
				all_stats[exchange_name]['paths'][path_key]['value'] *= path_stats['value'] / 100
				all_stats[exchange_name]['paths'][path_key]['value_fee_free'] *= path_stats['value_fee_free'] / 100
				all_stats[exchange_name]['paths'][path_key]['fees'] = all_stats[exchange_name]['paths'][path_key]['value_fee_free'] - all_stats[exchange_name]['paths'][path_key]['value']
				all_stats[exchange_name]['paths'][path_key]['last_value'] = path_stats['value']
				all_stats[exchange_name]['paths'][path_key]['last_value_fee_free'] = path_stats['value_fee_free']
				all_stats[exchange_name]['paths'][path_key]['last_fees'] = path_stats['value_fee_free'] - path_stats['value']

			# - save stats
			all_stats = {k:all_stats[k] for k in sorted(all_stats, key=lambda k: all_stats[k]['value'], reverse=True)}
			storage.save('all_stats', all_stats)

			# Finish
			strategy.finish()

		except Exception as e:
			exceptions = storage.get('exceptions') or {}
			if exchange_name not in exceptions:
				exceptions[exchange_name] = []

			# exceptions[exchange_name].append(str(e)[0:255])
			exceptions[exchange_name] = str(e)[0:255]
			storage.save('exceptions', exceptions)
