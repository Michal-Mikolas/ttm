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

		# From tickers
		try:
			tickers = Tools.get_tickers(exchange)
			for pair, ticker in tickers.items():
				if pair not in pairs:
					pairs[pair] = {'ticker': None, 'market': None, 'orderBook': None}

				pairs[pair]['ticker'] = ticker
		except ccxt.NotSupported as e:
			pass

		# From markets info
		try:
			markets = Tools.get_markets(exchange)
			for pair, market in markets.items():
				if pair not in pairs:
					pairs[pair] = {'ticker': None, 'market': None, 'orderBook': None}

				pairs[pair]['market'] = market
		except ccxt.NotSupported as e:
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

			if (not info['ticker']['bid'] or not info['ticker']['ask']) and not info['ticker']['last']:
				pairs.pop(pair)
				continue

			# Filter: Only active
			if info['market'] and ('active' in info['market']) and (info['market']['active'] == False):
				pairs.pop(pair)
				continue

			# Filter: Only 'spot' markets
			if info['market'] and ('type' in info['market']) and (info['market']['type'] != 'spot'):
				pairs.pop(pair)
				continue

			# Filter: Bittrex tokenized stocks are banned from normal trading
			if info['market'] and ('tags' in info['market']['info']) and ('TOKENIZED_SECURITY' in info['market']['info']['tags']):
				pairs.pop(pair)
				continue

			# Filter: Stex price multiplier is not implemented in TTM
			if info['market'] and ('amount_multiplier' in info['market']['info']) and (info['market']['info']['amount_multiplier'] != 1):
				pairs.pop(pair)
				continue

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

	def find_popular_quote(pairs, index=0):
		counter = {}
		for pair in pairs:
			pair = pair.split('/')

			if pair[1] not in counter:
				counter[pair[1]] = 0

			counter[pair[1]] += 1

		counter = {k:counter[k] for k in sorted(counter, key=counter.get, reverse=True)}

		if len(counter) > index:
			return list(counter.keys())[index]

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
