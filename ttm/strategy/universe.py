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

	def __init__(self, target: str, exchange_pairs: List, minimal_profit=1.0, path_length=4, tick_period=60, timeframe='1m'):
		super().__init__()

		# Config
		self.target = target
		self.exchange_pairs = self.parse_pairs(exchange_pairs)
		self.minimal_profit = minimal_profit  # percent
		self.path_length = path_length
		self.tick_period = tick_period        # seconds
		self.timeframe = timeframe

		# Initial calculations
		self.paths = self.build_paths()
		pprint(self.paths); pprint(len(self.paths))  ###
		self.prices = self.get_pairs_from_paths(self.paths)

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
				opened.pop(key, None)

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

	#######
	   #    #  ####  #    #
	   #    # #    # #   #
	   #    # #      ####
	   #    # #      #  #
	   #    # #    # #   #
	   #    #  ####  #    #

	def tick(self):
		self.update_prices()

		stats = self.calculate_path_stats()
		for key, values in stats.copy().items():
			if values['value'] < (1 + self.minimal_profit / 100):
				stats.pop(key)

		# stats = sorted(stats.items(), key=lambda stat: stat['value'])

		pprint(stats)

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
				# Price for exchange pair (buy)
				self.prices[pair] = tickers[pair]['ask']

				# Price for the mirror pair (sell)
				mirror_pair = self.exchange_pairs[pair][1] + '/' + self.exchange_pairs[pair][0]
				mirror_price = 1 / tickers[pair]['bid']

				self.prices[mirror_pair] = mirror_price

	def calculate_path_stats(self):
		path_stats = {}
		for path_key, path in self.paths.items():
			path_stats[path_key] = {'value': None}

			value = 1
			for i, symbol in enumerate(path):
				if len(path) >= (i+2):
					pair = path[i] + '/' + path[i+1]
					value = value / self.prices[pair]

			path_stats[path_key]['value'] = value

		return path_stats
