from datetime import datetime
from dateutil.parser import parse
from pprint import pprint
import ccxt

class Tools(object):

	def get_pairs(exchange):
		pairs = {}

		try:
			tickers = exchange.fetch_tickers()
		except (ccxt.NotSupported, ccxt.ExchangeNotAvailable):
			return Tools.get_pairs_using_markets(exchange)

		for pair, ticker in tickers.items():
			# Filter: Only standard pairs
			if '/' not in pair:
				continue

			# Filter: Only active pairs
			if not ticker['datetime']:
				continue

			if not ticker['bid'] or not ticker['ask']:
				continue

			now = datetime.now().timestamp()
			last_updated = exchange.parse8601(ticker['datetime']) / 1000
			passed = now - last_updated
			if passed > 10:
				continue

			# pprint(parse(ticker['datetime']).timestamp())
			# pprint(exchange.parse8601(ticker['datetime'])/1000)
			# pprint(datetime.now().timestamp())
			# print('------')

			# Save
			pairs[pair] = pair

		if len(pairs):
			return pairs.values()

		else:
			return Tools.get_pairs_using_markets(exchange)

	def get_pairs_using_markets(exchange, active = True, type = 'spot'):
		pairs = {}

		markets = exchange.fetch_markets()
		for market in markets:
			# Filter
			if active and ('active' in market) and (market['active'] != active):
				continue
			if type and ('type' in market) and (market['type'] != type):
				continue

			# Save
			symbol = market['symbol']
			pairs[symbol] = symbol

		return pairs.values()

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
