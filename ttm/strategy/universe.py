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

	def __init__(self, target: str, exchange_pairs: List, minimal_profit=1.0, path_length=4, tick_period=60):
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

	def set_bot(self, bot):
		self.bot = bot

	def find_paths(pairs, endpoint):
		pass
