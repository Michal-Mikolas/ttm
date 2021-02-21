from datetime import datetime
from dateutil.parser import parse
from pprint import pprint
import ccxt

class Tools(object):

	def get_pairs(exchange):
		#
		# 1) Get data
		#
		pairs = {}

		try:
			tickers = Tools.get_tickers(exchange)
			for pair, ticker in tickers.items():
				if pair not in pairs:
					pairs[pair] = {'ticker': None, 'market': None, 'orderBook': None}

				pairs[pair]['ticker'] = ticker
		except ccxt.NotSupported:
			pass

		try:
			markets = Tools.get_markets(exchange)
			for pair, market in markets.items():
				if pair not in pairs:
					pairs[pair] = {'ticker': None, 'market': None, 'orderBook': None}

				pairs[pair]['market'] = market
		except ccxt.NotSupported:
			pass

		#
		# 2) Filter only usable pairs
		#
		for pair, info in pairs.copy().items():
			# Filter: Only standard pairs
			if '/' not in pair:
				pairs.pop(pair)
				continue

			# Filter: Only pairs with known bid and ask prices
			if not info['ticker']:
				pairs.pop(pair)
				continue

			if not info['ticker']['bid'] or not info['ticker']['ask']:
				pairs.pop(pair)
				continue

			# Filter: Only not-too-old pairs
			# if not ticker['datetime']:
			# 	pairs.pop(pair)

			# if ticker['datetime']:
			# 	now = datetime.now().timestamp()
			# 	last_updated = exchange.parse8601(ticker['datetime']) / 1000
			# 	passed = now - last_updated
			# 	if passed > 10:
			# 		continue

			# 	# pprint(parse(ticker['datetime']).timestamp())
			# 	# pprint(exchange.parse8601(ticker['datetime'])/1000)
			# 	# pprint(datetime.now().timestamp())
			# 	# print('------')

			# Filter: Only active
			if info['market'] and ('active' in info['market']) and (info['market']['active'] == False):
				pairs.pop(pair)
				continue

			# Filter: Only 'spot' markets
			if info['market'] and ('type' in market) and (market['type'] != 'spot'):
				pairs.pop(pair)
				continue

			# # TODO Filtr: fetchOrderBook
			# try:
			# 	pairs[pair]['orderBook'] = exchange.fetch_order_book(pair)
			# except ccxt.NotSupported:
			# 	pass

		return pairs

	def get_tickers(exchange):
		pairs = {}

		tickers = exchange.fetch_tickers()
		for pair, ticker in tickers.items():
			pairs[pair] = ticker

		return pairs

	def get_markets(exchange, active=True, type='spot'):
		pairs = {}

		markets = exchange.fetch_markets()
		for market in markets:
			symbol = market['symbol']
			pairs[symbol] = market

		return pairs

	def find_popular_base(pairs):
		counter = {}
		for pair in pairs:
			pair = pair.split('/')

			if pair[1] not in counter:
				counter[pair[1]] = 0

			counter[pair[1]] += 1

		counter = {k:counter[k] for k in sorted(counter, key=counter.get)}

		if len(counter):
			return list(counter.keys())[-1]

		else:
			return None

	def get_class(kls):
		# @see https://stackoverflow.com/questions/452969/does-python-have-an-equivalent-to-java-class-forname
		parts = kls.split('.')
		module = ".".join(parts[:-1])
		m = __import__(module)
		for comp in parts[1:]:
			m = getattr(m, comp)
		return m
