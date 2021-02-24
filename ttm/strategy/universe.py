from typing import List
import ccxt
from datetime import datetime
from ttm.strategy import Strategy
import re
from pprint import pprint

"""
(This file is part of TTM package)

TTM - ToTheMoon crypto trading bot

@author  Michal Mikolas (nanuqcz@gmail.com)
"""
class Universe(Strategy):

	###
	 #  #    # # #####
	 #  ##   # #   #
	 #  # #  # #   #
	 #  #  # # #   #
	 #  #   ## #   #
	### #    # #   #

	def __init__(self,
		target: str,
		exchange_pairs: List,
		minimal_profit=1.01,
		path_length=4,
		tick_period=5
	):
		super().__init__()

		# Config
		self.target = target
		self.exchange_pairs = self.parse_pairs(exchange_pairs)
		self.minimal_profit = minimal_profit  # percent
		self.path_length = path_length
		self.tick_period = tick_period        # seconds

		self.scanner = UniverseScanner()

		# Initial calculations
		self.paths = self.build_paths()
		# print('# PATHS') ; pprint(self.paths); pprint(len(self.paths))  ###
		self.prices = self.get_pairs_from_paths(self.paths)

	def set_bot(self, bot):
		super().set_bot(bot)
		self.scanner.set_bot(bot)

	def parse_pairs(self, pairs: List):
		result = {}

		for pair in pairs:
			result[pair] = pair.split('/')

		return result

	######
	#     #   ##   ##### #    #  ####
	#     #  #  #    #   #    # #
	######  #    #   #   ######  ####
	#       ######   #   #    #      #
	#       #    #   #   #    # #    #
	#       #    #   #   #    #  ####

	def build_paths(self):
		pairs = self.get_two_way_pairs()

		#
		# 1. Find all possible closed paths
		#
		closed = {}
		opened = {self.target: [self.target]}
		while len(opened) > 0:
			# For each path in `opened` list:
			for key, path in opened.copy().items():
				# If it is closed, move it to `closed` list
				if (len(path) > 2) and (path[-1] == self.target):
					closed[key] = path
					opened.pop(key)
					break

				# Else try to find a way to continue
				for name, currencies in pairs.items():
					if currencies[0] == path[-1]:
						# possible continuation found, create new entry
						new_path = path.copy()
						new_path.append(currencies[1])

						if len(new_path) <= self.path_length:
							opened['-'.join(new_path)] = new_path

				# We tried hard to find the continuation, so don't try again
				opened.pop(key)

		#
		# 2. Filter `closed` list
		#
		for key, path in closed.copy().items():
			if len(path) <= 3:
				closed.pop(key)

		#
		# 3. Return
		#
		return closed

	def get_two_way_pairs(self):
		result = {}

		for name, currencies in self.exchange_pairs.items():
			result[name] = currencies
			result[currencies[1] + '/' + currencies[0]] = [currencies[1], currencies[0]]

		return result

	def get_pairs_from_paths(self, paths):
		pairs = {}
		for key, path in paths.items():
			for i, symbol in enumerate(path):
				if len(path) >= (i+2):
					pair = path[i] + '/' + path[i+1]
					pairs[pair] = pair

		return pairs

	def unmirror_pair(self, pair):
		if pair not in self.exchange_pairs:
			symbols = pair.split('/')
			pair = symbols[1] + '/' + symbols[0]

		return pair

	def fetch_stats_order_books(self, stats):
		for key, stat in stats.copy().items():
			for i, symbol in enumerate(stat['path']):
				if len(stat['path']) >= (i+2):
					pair = self.unmirror_pair(stat['path'][i+1] + '/' + stat['path'][i])

					if 'orderBooks' not in stat:
						stat['orderBooks'] = {}
					stat['orderBooks'][pair] = self.bot.exchange.fetch_order_book(pair)

		return stats

	#######
	   #    #  ####  #    #
	   #    # #    # #   #
	   #    # #      ####
	   #    # #      #  #
	   #    # #    # #   #
	   #    #  ####  #    #

	def tick(self):
		# paths = self.scanner.full_scan(
		# 	self.exchange_pairs,
		# 	endpoint=self.target,
		# 	min_value_after_fees=1.01,  # 101 %
		# 	min_bids_count=12,
		# 	min_asks_count=12,
		# )


		#
		# Get current data
		#

		# Refresh prices
		self.update_prices()

		# Create paths statistics
		stats = self.calculate_path_stats()

		#
		# Filter
		#

		# Filter: Only paths with required profit
		for key, stat in stats.copy().items():
			if stat['value'] < (100 + self.minimal_profit):
				stats.pop(key)

		# Filter: Only paths with proper order book
		stats = self.fetch_stats_order_books(stats)
		for key, stat in stats.copy().items():
			for pair, order_book in stat['orderBooks'].items():
				if len(order_book['bids']) < 12:  ###
					print("%s orderBook has only %d bids." % (pair, len(order_book['bids'])))
				if len(order_book['asks']) < 12:  ###
					print("%s orderBook has only %d asks." % (pair, len(order_book['asks'])))

				if len(order_book['bids']) < 12 or len(order_book['asks']) < 12:
					stats.pop(key)
					break

		#
		# Finish
		#
		stats = {k:stats[k] for k in sorted(stats, key=lambda k: stats[k]['value'], reverse=True)}
		# self.bot.storage.save('stats', stats)  ###
		# pprint(stats)  ###
		# exit()  ###

		return stats

	######
	#     # #####  #  ####  ######  ####
	#     # #    # # #    # #      #
	######  #    # # #      #####   ####
	#       #####  # #      #           #
	#       #   #  # #    # #      #    #
	#       #    # #  ####  ######  ####

	def update_prices(self):
		# Clear old prices
		for pair, price in self.prices.items():
			self.prices[pair] = None

		# Download current prices
		tickers = self.bot.get_tickers(self.exchange_pairs.keys())

		# Save prices to the list
		for pair, price in self.prices.items():
			if pair in self.exchange_pairs:
				# Check
				if pair not in tickers:
					continue
				if not tickers[pair]['ask'] or not tickers[pair]['bid']:
					continue

				# Price for exchange pair (buy)
				self.prices[pair] = tickers[pair]['ask']

				# Price for the mirror pair (sell)
				mirror_pair = self.exchange_pairs[pair][1] + '/' + self.exchange_pairs[pair][0]
				mirror_price = 1 / tickers[pair]['bid']

				self.prices[mirror_pair] = mirror_price

	def calculate_path_stats(self):
		path_stats = {}
		for path_key, path in self.paths.items():
			path_stats[path_key] = {
				'path': path,
				'value': None,
				'value_fee_free': None,
				'steps': [],
				'orderBooks': {}
			}

			try:
				value = 100
				value_fee_free = 100
				path_stats[path_key]['steps'].append('%s: %f' % (path[0], value))
				for i, symbol in enumerate(path):
					if len(path) >= (i+2):
						pair = path[i+1] + '/' + path[i]
						path_stats[path_key]['steps'].append('(%s = %f)' % (pair, self.prices[pair]))

						# Value including fee
						path_stats[path_key]['steps'].append('%s: %f / %f = %f' % (path[i+1], value, self.prices[pair], value / self.prices[pair]))
						value = value / self.prices[pair]

						fee_percent = self.get_fee(pair)
						path_stats[path_key]['steps'].append('%s: %f * (1 - %f / 100) = %f' % (path[i+1], value, fee_percent, value * (1 - fee_percent / 100)))
						fee = value * fee_percent / 100
						value -= fee

						# Value fee-free
						value_fee_free = value_fee_free / self.prices[pair]

				path_stats[path_key]['value'] = value
				path_stats[path_key]['value_fee_free'] = value_fee_free

			except TypeError:  # self.prices[pair] is None
				path_stats.pop(path_key)

		return path_stats

	def get_fee(self, pair):
		if pair in self.exchange_pairs:
			info = self.bot.exchange.market(pair)
			return info['taker'] * 100

		else:
			symbols = pair.split('/')
			pair = "%s/%s" % (symbols[1], symbols[0])
			info = self.bot.exchange.market(pair)
			return info['maker'] * 100


 #####
#     #  ####    ##   #    # #    # ###### #####
#       #    #  #  #  ##   # ##   # #      #    #
 #####  #      #    # # #  # # #  # #####  #    #
      # #      ###### #  # # #  # # #      #####
#     # #    # #    # #   ## #   ## #      #   #
 #####   ####  #    # #    # #    # ###### #    #

class UniverseScanner(object):

	def __init__(self):
		self.bot = None
		self.cache = {}

	def set_bot(self, bot):
		self.bot = bot

	def full_scan(self, exchange_pairs, endpoint,
        path_length = 4,
		min_value_after_fees = 1.0,
		min_bids_count = 1,
		min_asks_count = 1,
		trade_amount = None,
	):
		# 1. Get basic paths & statistics
		paths = self.trace_paths(exchange_pairs, endpoint, path_length)
		paths = self.fill_statistics(paths, exchange_pairs)

		# 2. Filter by basic statistics
		for path_key, path_data in paths.copy().items():
			if min_value_after_fees and (path_data['value'] < min_value_after_fees):
				paths.pop(path_key)
				continue

		# 3. Add more data
		for path_key, path_data in paths.copy().items():

			symbols = path_data['symbols']
			for i, symbol in enumerate(symbols):
				if len(symbols) >= (i+2):
					# find proper pair supported by exchange
					pair = symbols[i+1] + '/' + symbols[i]
					if pair not in exchange_pairs:
						pair = symbols[i] + '/' + symbols[i+1]

					# fetch pair order_book
					path_data['order_books'][pair] = self.bot.exchange.fetch_order_book(pair)

		# 4. Filter by more data
		for path_key, path_data in paths.copy().items():
			for pair_key, order_book in path_data['order_books'].items():
				# bids count
				if min_bids_count and (len(order_book['bids']) < min_bids_count):
					paths.pop(path_key)
					break

				# asks count
				if min_asks_count and (len(order_book['asks']) < min_asks_count):
					paths.pop(path_key)
					break

		# 5. Simulation based on order_book
		if trade_amount:
			for path_key, path_data in paths.copy().items():
				# Add simulation results
				path_data['simulation'] = self.simulate(path_data, trade_amount, exchange_pairs)

				# Filter by simulation results
				simulation_value = path_data['simulation'][-1]['result_value'] / trade_amount
				if simulation_value < min_value_after_fees:
					paths.pop(path_key)
					continue

		# 6. Finish
		paths = {k:paths[k] for k in sorted(paths, key=lambda k: paths[k]['value'], reverse=True)}

		return paths

	def trace_paths(self, pairs, endpoint, path_length=4):
		if 'trace_paths' not in self.cache:
			pairs = self.get_two_way_pairs(pairs)

			#
			# 1. Find all possible closed paths
			#
			closed = {}
			opened = {endpoint: [endpoint]}
			while len(opened) > 0:
				# For each path in `opened` list:
				for path_key, path_symbols in opened.copy().items():
					# If it is closed, move it to `closed` list
					if (len(path_symbols) > 2) and (path_symbols[-1] == endpoint):
						closed[path_key] = path_symbols
						opened.pop(path_key)
						break

					# Else try to find a way to continue
					for pair_name, pair_symbols in pairs.items():
						if pair_symbols[0] == path_symbols[-1]:
							# possible continuation found, create new entry
							new_path_symbols = path_symbols.copy()
							new_path_symbols.append(pair_symbols[1])

							if len(new_path_symbols) <= path_length:
								opened['-'.join(new_path_symbols)] = new_path_symbols

					# We tried hard to find the continuation, so don't try again
					opened.pop(path_key)

			#
			# 2. Filter non-sences in `closed` list
			#
			for path_key, path_symbols in closed.copy().items():
				if len(path_symbols) <= 3:
					closed.pop(path_key)

			#
			# 3. Add structure for future statistics
			#
			for path_key, path_symbols in closed.copy().items():
				closed[path_key] = {
					'symbols': path_symbols,
					'value': None,
					'value_fee_free': None,
					'steps': [],
					'order_books': {},
					'simulation': [],
				}

			#
			# 4. Finish
			#
			self.cache['trace_paths'] = closed

		return self.cache['trace_paths'].copy()

	def get_two_way_pairs(self, pairs):
		result = {}

		for pair_name in pairs:
			symbols = pair_name.split('/')

			result[pair_name] = symbols
			result[symbols[1] + '/' + symbols[0]] = [symbols[1], symbols[0]]

		return result

	def fill_statistics(self, paths, exchange_pairs):
		prices = self.get_prices(exchange_pairs)

		# For every path...
		for path_key, path_data in paths.copy().items():
			path_data['steps'].append({
				'type': 'initial',
				'pair': None,
				'price': None,
				'formula': None,
				'formula_fee_free': None,
				'result_value': 1.0,
				'result_value_fee_free': 1.0,
				'result_currency': path_data['symbols'][0],
			})

			# Go through every currency pair
			# try:
			for i, symbol in enumerate(path_data['symbols']):
				if len(path_data['symbols']) >= (i+2):
					# And simulate the buy/sell process.
					last_step = path_data['steps'][-1]
					current_step = {
						'type': None,
						'pair': None,
						'price': None,
						'formula': None,
						'formula_fee_free': None,
						'result_value': None,
						'result_value_fee_free': None,
						'result_currency': path_data['symbols'][i+1],
					}

					pair = path_data['symbols'][i+1] + '/' + path_data['symbols'][i]
					fee_percent = self.get_fee(pair, exchange_pairs)
					fee_koef = fee_percent / 100
					if pair in exchange_pairs:
						# Buy
						current_step['type'] = 'buy'
						current_step['pair'] = pair
						current_step['price'] = prices[pair]['ask']
						current_step['formula'] = "%f / %f * (1 - %f)" % (
							last_step['result_value'],
							prices[pair]['ask'],
							fee_koef,
						)
						current_step['formula_fee_free'] = "%f / %f" % (
							last_step['result_value_fee_free'],
							prices[pair]['ask'],
						)
						current_step['result_value'] = last_step['result_value'] / prices[pair]['ask'] * (1 - fee_koef)
						current_step['result_value_fee_free'] = last_step['result_value_fee_free'] / prices[pair]['ask']
					else:
						# Sell
						pair = path_data['symbols'][i] + '/' + path_data['symbols'][i+1]
						current_step['type'] = 'sell'
						current_step['pair'] = pair
						current_step['price'] = prices[pair]['bid']
						current_step['formula'] = "%f * %f * (1 - %f)" % (
							last_step['result_value'],
							prices[pair]['bid'],
							fee_koef,
						)
						current_step['formula_fee_free'] = "%f * %f" % (
							last_step['result_value_fee_free'],
							prices[pair]['bid'],
						)
						current_step['result_value'] = last_step['result_value'] * prices[pair]['bid'] * (1 - fee_koef)
						current_step['result_value_fee_free'] = last_step['result_value_fee_free'] * prices[pair]['bid']

					path_data['steps'].append(current_step)

			# Save final values
			path_data['value'] = current_step['result_value']
			path_data['value_fee_free'] = current_step['result_value_fee_free']

			# except TypeError:  # prices[pair] is not set
			# 	# If can't get price for a pair, discard whole path
			# 	paths.pop(path_key)

		# Return results
		return paths

	def get_fee(self, pair, exchange_pairs):
		cache_key = "get_fee-" + pair

		if cache_key not in self.cache:
			if pair in exchange_pairs:
				info = self.bot.exchange.market(pair)
				self.cache[cache_key] = info['taker'] * 100

			else:
				symbols = pair.split('/')
				pair = "%s/%s" % (symbols[1], symbols[0])
				info = self.bot.exchange.market(pair)
				self.cache[cache_key] = info['maker'] * 100

		return self.cache[cache_key]

	def get_prices(self, pairs):
		prices = {}

		# Download current prices
		tickers = self.bot.get_tickers(pairs.keys())

		# Save prices to the list
		for pair in pairs:
			# Check
			if pair not in tickers:
				continue
			if not tickers[pair]['ask'] or not tickers[pair]['bid']:
				continue
			if tickers[pair]['ask'] < tickers[pair]['bid']:
				print(" ! WARNING: %s: Weird universe occured, 'ask' price (%f) is lower than 'bid' price (%f)." % (pair, tickers[pair]['ask'], tickers[pair]['bid']))

			prices[pair] = {
				'ask': tickers[pair]['ask'],
				'bid': tickers[pair]['bid'],
			}

		return prices

	def simulate(self, path_data, trade_amount, exchange_pairs):
		path_data['simulation'].append({
			'type': 'initial',
			'pair': None,
			'price': None,
			'formula': None,
			'formula_fee_free': None,
			'result_value': trade_amount,
			'result_value_fee_free': trade_amount,
			'result_currency': path_data['symbols'][0],
		})

		# Go through every currency pair
		# try:
		for i, symbol in enumerate(path_data['symbols']):
			if len(path_data['symbols']) >= (i+2):
				# And simulate the buy/sell process.
				last_step = path_data['simulation'][-1]
				current_step = {
					'type': None,
					'pair': None,
					'price': None,
					'formula': None,
					'formula_fee_free': None,
					'result_value': None,
					'result_value_fee_free': None,
					'result_currency': path_data['symbols'][i+1],
				}

				pair = path_data['symbols'][i+1] + '/' + path_data['symbols'][i]
				fee_percent = self.get_fee(pair, exchange_pairs)
				fee_koef = fee_percent / 100
				if pair in exchange_pairs:
					# Buy
					result_value = 0
					result_value_fee_free = 0
					money_left = last_step['result_value']
					for price, amount in path_data['order_books'][pair]['asks']:
						needed_amount = money_left / price
						if needed_amount > amount:
							result_value += amount * (1 - fee_koef)
							money_left -= amount * price

						if needed_amount <= amount:
							result_value += needed_amount * (1 - fee_koef)
							money_left = 0

						if money_left == 0:
							break


					current_step['type'] = 'buy'
					current_step['pair'] = pair
					current_step['result_value'] = last_step['result_value'] / prices[pair]['ask'] * (1 - fee_koef)
					current_step['result_value_fee_free'] = last_step['result_value_fee_free'] / prices[pair]['ask']
				else:
					# Sell
					pair = path_data['symbols'][i] + '/' + path_data['symbols'][i+1]
					current_step['type'] = 'sell'
					current_step['pair'] = pair
					current_step['result_value'] = last_step['result_value'] * prices[pair]['bid'] * (1 - fee_koef)
					current_step['result_value_fee_free'] = last_step['result_value_fee_free'] * prices[pair]['bid']

				path_data['simulation'].append(current_step)

		# Finish
		return path_data['simulation']
