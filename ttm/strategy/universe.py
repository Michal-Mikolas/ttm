from typing import List
from datetime import datetime
import time
from ttm.strategy import Strategy
from pprint import pprint

"""
(This file is part of TTM package)

TTM - ToTheMoon crypto trading bot

@author  Michal Mikolas (nanuqcz@gmail.com)
"""



#     #
#     # #    # # #    # ###### #####   ####  ######
#     # ##   # # #    # #      #    # #      #
#     # # #  # # #    # #####  #    #  ####  #####
#     # #  # # # #    # #      #####       # #
#     # #   ## #  #  #  #      #   #  #    # #
 #####  #    # #   ##   ###### #    #  ####  ######

class Universe(Strategy):

	###
	 #  #    # # #####
	 #  ##   # #   #
	 #  # #  # #   #
	 #  #  # # #   #
	 #  #   ## #   #
	### #    # #   #

	def __init__(self,
		endpoint: str,
		exchange_pairs: List,
		executor,
		minimal_value=1.01,
		minimal_worse_value=1.01,
		path_length=4,
		tick_period=5,
		limits: dict = {},
		min_bids_count=3,
		min_asks_count=3,
	):
		super().__init__()

		# Config
		self.endpoint = endpoint
		self.exchange_pairs = self.parse_pairs(exchange_pairs)
		self.executor = executor
		self.minimal_value = minimal_value
		self.minimal_worse_value = minimal_worse_value
		self.path_length = path_length
		self.tick_period = tick_period      # seconds
		self.limits = limits
		self.min_bids_count = min_bids_count
		self.min_asks_count = min_asks_count

		self.executor.set_strategy(self)

		self.scanner = UniverseScanner()

	def set_bot(self, bot):
		super().set_bot(bot)
		self.executor.set_bot(bot)
		self.scanner.set_bot(bot)

	def parse_pairs(self, pairs: List):
		result = {}

		for pair in pairs:
			result[pair] = pair.split('/')

		return result

	def limit(self, amount, symbol):
		if (symbol in self.limits) and (amount > self.limits[symbol]):
			amount = self.limits[self.endpoint]

		return amount

	#######
	   #    #  ####  #    #
	   #    # #    # #   #
	   #    # #      ####
	   #    # #      #  #
	   #    # #    # #   #
	   #    #  ####  #    #

	def tick(self):
		#
		# Prepare
		#
		balance_before = self.bot.get_balance(self.endpoint)
		trade_amount = self.limit(balance_before, self.endpoint)

		#
		# Scan for available paths
		#
		paths = self.scanner.full_scan(
			exchange_pairs        = self.exchange_pairs,
			endpoint              = self.endpoint,
			path_length           = self.path_length,
			trade_amount          = trade_amount,
			min_result_after_fees = trade_amount * self.minimal_value,
			min_worse_result      = trade_amount * self.minimal_worse_value,
			min_bids_count        = self.min_bids_count,
			min_asks_count        = self.min_asks_count,
		)

		if len(paths):
			# Find the most profitable path
			path_key = max(paths, key=lambda k: paths[k]['simulation'][-1]['result_amount'])
			path_data = paths[path_key]
			expected_value = path_data['simulation'][-1]['result_amount'] / path_data['simulation'][0]['result_amount']

			self.bot.log(
				"Found path %s, expected value: %f" % (path_key, expected_value),
				priority=1,
				extra_values=False
			)
			self.bot.storage.save(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), {
				'path_key': path_key,
				'balance_before': balance_before,
				'balance_after': None,
				'path_data': path_data,
			})

			#
			# Let's realize the simulation
			#
			# for i, step in enumerate(path_data['simulation']):
			# 	self.executor.execute(
			# 		simulation = path_data['simulation'],
			# 		index = i
			# 	)

			#
			# Log the results
			#
			balance_after = self.bot.get_balance(self.endpoint)
			self.bot.log(
				"%s finished; Coef expected / real: %f / %f; Balance before / after: %f / %f" % (
					path_key,
					expected_value,
					balance_after / balance_before,
					balance_before,
					balance_after,
				),
				priority=2,
				extra_values=False
			)
			self.bot.storage.save(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), {
				'path_key': path_key,
				'balance_before': balance_before,
				'balance_after': balance_after,
				'path_data': path_data,
			})






#######
#       #    # ######  ####  #    # #####  ####  #####   ####
#        #  #  #      #    # #    #   #   #    # #    # #
#####     ##   #####  #      #    #   #   #    # #    #  ####
#         ##   #      #      #    #   #   #    # #####       #
#        #  #  #      #    # #    #   #   #    # #   #  #    #
####### #    # ######  ####   ####    #    ####  #    #  ####

class Executor(object):
	def __init__(self, order_timeout=10):
		self.bot = None
		self.strategy = None
		self.order_timeout = order_timeout

	def set_bot(self, bot):
		self.bot = bot

	def set_strategy(self, strategy):
		self.strategy = strategy

	def execute(self, simulation: list, index: int):
		pass

	def wait_for_orders(self, pair: str, since=None, limit=None):
		for i in range(self.order_timeout):
			orders = self.bot.get_open_orders(pair, since, limit)
			if len(orders) == 0:
				time.sleep(1)
				return True

			time.sleep(1)

		raise TimeoutError("Order %s not closed after %d seconds." % (pair, self.order_timeout))


class MarketExecutor(Executor):
	def execute(self, simulation: list, index: int):
		step = simulation[index]

		if step['type'] not in ['buy', 'sell']:
			return

		# Prepare
		pair_str = step['pair']
		pair = pair_str.split('/')

		# Buy
		if step['type'] == 'buy':
			balance = self.bot.get_balance(pair[1])
			self.bot.log(
				"%s balance: %f" % (pair[1], balance),
				priority=1,
				extra_values=False
			)
			quote = self.strategy.limit(
				balance,
				pair[1]
			)

			self.bot.log(
				"Buying %s; Cost: %f" % (pair_str, quote),
				priority=1,
				extra_values=False
			)
			self.bot.buy(pair_str, cost=quote)

			self.wait_for_orders(pair_str)

		# Sell
		if step['type'] == 'sell':
			balance = self.bot.get_balance(pair[0])
			self.bot.log(
				"%s balance: %f" % (pair[0], balance),
				priority=1,
				extra_values=False
			)
			base = self.strategy.limit(
				balance,
				pair[0]
			)

			self.bot.log(
				"Selling %s; Base: %f" % (pair_str, base),
				priority=1,
				extra_values=False
			)
			self.bot.sell(pair_str, base)

			self.wait_for_orders(pair_str)


class WorsePriceExecutor(Executor):
	def execute(self, simulation: list, index: int):
		step = simulation[index]

		# Prepare
		pair_str = step['pair']
		pair = pair_str.split('/')

		expected_value = simulation[-1]['result_amount'] / simulation[0]['result_amount']
		best_price = step['transactions'][1]['price']
		worst_price = step['transactions'][-1]['price']
		self.bot.log(
			"Price (best / worst): %f / %f" % (best_price, worst_price),
			priority=1,
			extra_values=False
		)

		# Buy
		if step['type'] == 'buy':
			# worst_price = worst_price * expected_value
			self.bot.log(
				"Changing worst price to %f" % (worst_price),
				priority=1,
				extra_values=False
			)

			balance = self.bot.get_balance(pair[1])
			self.bot.log(
				"%s balance: %f" % (pair[1], balance),
				priority=1,
				extra_values=False
			)
			quote = self.strategy.limit(
				balance,
				pair[1]
			)
			base = quote / worst_price

			self.bot.log(
				"Buying %s; Base: %f; Quote: %f; Price: %f" % (pair_str, base, quote, worst_price),
				priority=1,
				extra_values=False
			)
			self.bot.buy(pair_str, base, worst_price)

			self.wait_for_orders(pair_str)

		# Sell
		if step['type'] == 'sell':
			# worst_price = worst_price / expected_value
			self.bot.log(
				"Changing worst price to %f" % (worst_price),
				priority=1,
				extra_values=False
			)

			balance = self.bot.get_balance(pair[0])
			self.bot.log(
				"%s balance: %f" % (pair[0], balance),
				priority=1,
				extra_values=False
			)
			base = self.strategy.limit(
				balance,
				pair[0]
			)

			self.bot.log(
				"Selling %s; Base: %f; Price: %f" % (pair_str, base, worst_price),
				priority=1,
				extra_values=False
			)
			self.bot.sell(pair_str, base, worst_price)

			self.wait_for_orders(pair_str)


class HybridExecutor(Executor):
	def execute(self, simulation: list, index: int):
		step = simulation[index]

		# Prepare
		pair_str = step['pair']
		pair = pair_str.split('/')

		expected_value = simulation[-1]['result_amount'] / simulation[0]['result_amount']
		best_price = step['transactions'][1]['price']
		worst_price = step['transactions'][-1]['price']
		self.bot.log(
			"Price (best / worst): %f / %f" % (best_price, worst_price),
			priority=1,
			extra_values=False
		)

		# Buy (worst_price type)
		if step['type'] == 'buy':
			# worst_price = worst_price * expected_value
			self.bot.log(
				"Changing worst price to %f" % (worst_price),
				priority=1,
				extra_values=False
			)

			balance = self.bot.get_balance(pair[1])
			self.bot.log(
				"%s balance: %f" % (pair[1], balance),
				priority=1,
				extra_values=False
			)
			quote = self.strategy.limit(
				balance,
				pair[1]
			)
			base = quote / worst_price

			self.bot.log(
				"Buying %s; Base: %f; Quote: %f; Price: %f" % (pair_str, base, quote, worst_price),
				priority=1,
				extra_values=False
			)
			self.bot.buy(pair_str, base, worst_price)

			self.wait_for_orders(pair_str)

		# Sell (market type)
		if step['type'] == 'sell':
			balance = self.bot.get_balance(pair[0])
			self.bot.log(
				"%s balance: %f" % (pair[0], balance),
				priority=1,
				extra_values=False
			)
			base = self.strategy.limit(
				balance,
				pair[0]
			)

			self.bot.log(
				"Selling %s; Base: %f" % (pair_str, base),
				priority=1,
				extra_values=False
			)
			self.bot.sell(pair_str, base)

			self.wait_for_orders(pair_str)






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
		trade_amount = 1.0,
		min_result_after_fees = 1.0,
		min_worse_result = 1.0,
		min_bids_count = 1,
		min_asks_count = 1,
	):
		# 1. Get basic paths & statistics
		paths = self.trace_paths(exchange_pairs, endpoint, path_length)
		paths = self.guess_paths_results(paths, exchange_pairs, trade_amount)

		# 2. Filter by basic statistics
		for path_key, path_data in paths.copy().items():
			if min_result_after_fees and (path_data['result_amount'] < min_result_after_fees):
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

		# 5. Create simulation based on order_book
		if trade_amount:
			for path_key, path_data in paths.copy().items():
				path_data['simulation'] = self.simulate_path(path_data, trade_amount, exchange_pairs)

		# 6. Filter by simulation results
		if trade_amount:
			for path_key, path_data in paths.copy().items():

				if min_result_after_fees and (path_data['simulation'][-1]['result_amount'] < min_result_after_fees):
					paths.pop(path_key)
					continue

				if min_worse_result and (path_data['simulation'][-1]['worse_result_amount'] < min_worse_result):
					paths.pop(path_key)
					continue

		# 6. Finish
		paths = {k:paths[k] for k in sorted(paths, key=lambda k: paths[k]['simulation'][-1]['worse_result_amount'], reverse=True)}

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
					'result_amount': None,
					'result_amount_fee_free': None,
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

	def guess_paths_results(self, paths, exchange_pairs, trade_amount=1.0):
		prices = self.get_prices(exchange_pairs)

		# For every path...
		for path_key, path_data in paths.copy().items():
			path_data['steps'].append({
				'type': 'initial',
				'pair': None,
				'price': None,
				'formula': None,
				'formula_fee_free': None,
				'result_amount': trade_amount,
				'result_amount_fee_free': trade_amount,
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
						'result_amount': None,
						'result_amount_fee_free': None,
						'result_currency': path_data['symbols'][i+1],
					}

					pair = path_data['symbols'][i+1] + '/' + path_data['symbols'][i]
					fee_percent = self.get_buy_fee(pair, exchange_pairs)
					fee_koef = fee_percent / 100
					if pair in exchange_pairs:
						# Buy
						current_step['type'] = 'buy'
						current_step['pair'] = pair
						current_step['price'] = prices[pair]['ask']
						current_step['formula'] = "%f / %f * (1 - %f)" % (
							last_step['result_amount'],
							prices[pair]['ask'],
							fee_koef,
						)
						current_step['formula_fee_free'] = "%f / %f" % (
							last_step['result_amount_fee_free'],
							prices[pair]['ask'],
						)
						current_step['result_amount'] = last_step['result_amount'] / prices[pair]['ask'] * (1 - fee_koef)
						current_step['result_amount_fee_free'] = last_step['result_amount_fee_free'] / prices[pair]['ask']
					else:
						# Sell
						pair = path_data['symbols'][i] + '/' + path_data['symbols'][i+1]
						current_step['type'] = 'sell'
						current_step['pair'] = pair
						current_step['price'] = prices[pair]['bid']
						current_step['formula'] = "%f * %f * (1 - %f)" % (
							last_step['result_amount'],
							prices[pair]['bid'],
							fee_koef,
						)
						current_step['formula_fee_free'] = "%f * %f" % (
							last_step['result_amount_fee_free'],
							prices[pair]['bid'],
						)
						current_step['result_amount'] = last_step['result_amount'] * prices[pair]['bid'] * (1 - fee_koef)
						current_step['result_amount_fee_free'] = last_step['result_amount_fee_free'] * prices[pair]['bid']

					path_data['steps'].append(current_step)

			# Save final amounts
			path_data['result_amount'] = current_step['result_amount']
			path_data['result_amount_fee_free'] = current_step['result_amount_fee_free']

			# except TypeError:  # prices[pair] is not set
			# 	# If can't get price for a pair, discard whole path
			# 	paths.pop(path_key)

		# Return results
		return paths

	def get_buy_fee(self, pair, exchange_pairs):
		cache_key = "get_buy_fee-" + pair

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
			tickers[pair]['ask'] = tickers[pair]['ask'] or tickers[pair]['last']  # not all exchanges give you ask and bid prices
			tickers[pair]['bid'] = tickers[pair]['bid'] or tickers[pair]['last']

			# Check
			if pair not in tickers:
				continue
			if not tickers[pair]['ask'] or not tickers[pair]['bid']:
				continue
			if tickers[pair]['ask'] < tickers[pair]['bid']:
				print(" ! WARNING: %s: Weird universe occured, 'ask' price (%f) is lower than 'bid' price (%f)." % (pair, tickers[pair]['ask'], tickers[pair]['bid']))
				tickers[pair]['ask'], tickers[pair]['bid'] = tickers[pair]['bid'], tickers[pair]['ask']

			prices[pair] = {
				'ask': tickers[pair]['ask'],
				'bid': tickers[pair]['bid'],
			}

		return prices

	def simulate_path(self, path_data, trade_amount, exchange_pairs):
		path_data['simulation'].append({
			'type': 'initial',
			'pair': None,
			'transactions': [],
			'result_amount': trade_amount,
			'worse_result_amount': trade_amount,
			'result_symbol': path_data['symbols'][0],
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
					'transactions': [],
					'result_amount': None,
					'worse_result_amount': None,
					'result_symbol': path_data['symbols'][i+1],
				}

				pair = path_data['symbols'][i+1] + '/' + path_data['symbols'][i]
				fee_percent = self.get_buy_fee(pair, exchange_pairs)  # automatically transform into 'sell fee' if necessary
				if pair in exchange_pairs:
					# Buy
					current_step['type'] = 'buy'
					current_step['pair'] = pair

					current_step['transactions'] = self.simulate_buy_transactions(
						quote=last_step['result_amount'],
						offers=path_data['order_books'][pair]['asks'],
						fee_percent=fee_percent,
						worse_quote=last_step['worse_result_amount'],
					)

					current_step['result_amount'] = current_step['transactions'][-1]['result_base']
					current_step['worse_result_amount'] = current_step['transactions'][-1]['worse_result_base']

				else:
					# Sell
					pair = path_data['symbols'][i] + '/' + path_data['symbols'][i+1]
					current_step['type'] = 'sell'
					current_step['pair'] = pair

					current_step['transactions'] = self.simulate_sell_transactions(
						base=last_step['result_amount'],
						offers=path_data['order_books'][pair]['bids'],
						fee_percent=fee_percent,
						worse_base=last_step['worse_result_amount'],
					)

					current_step['result_amount'] = current_step['transactions'][-1]['result_quote']
					current_step['worse_result_amount'] = current_step['transactions'][-1]['worse_result_quote']

				path_data['simulation'].append(current_step)

		# Finish
		return path_data['simulation']

	def simulate_buy_transactions(self, quote:float, offers:list, fee_percent = 0.0, worse_quote:float = None):
		offers = [v for v in sorted(offers, key=lambda v: v[0])]
		base = 0.0
		quote = quote * (1 - fee_percent / 100)
		worse_quote = worse_quote * (1 - fee_percent / 100)

		transactions = []
		transactions.append({
			'type': 'initial',
			'change_base': 0.0,
			'change_quote': 0.0,
			'result_base': 0.0,
			'result_quote': quote,
			'worse_result_quote': worse_quote,
		})

		#
		# Ideal buy
		# (use all cheap offers)
		#
		for offer_price, offer_base in offers:
			claimed_base = quote / offer_price

			# not enough base available, buy what you can
			if claimed_base > offer_base:
				base += offer_base
				quote -= offer_base * offer_price

				transactions.append({
					'type': 'buy',
					'price': offer_price,
					'available_amount': offer_base,
					'change_base': offer_base,
					'change_quote': -1 * offer_base * offer_price,
					'result_base': base,
					'result_quote': quote,
					'worse_result_base': 0.0,
				})

			# all wanted base can be bought
			if claimed_base <= offer_base:
				base += claimed_base
				quote = 0.0

				transactions.append({
					'type': 'buy',
					'price': offer_price,
					'available_amount': offer_base,
					'change_base': claimed_base,
					'change_quote': -1 * claimed_base * offer_price,
					'result_base': base,
					'result_quote': quote,
					'worse_result_base': 0.0,
				})

			# no quote left, finish
			if quote == 0:
				break

		#
		# Worse buy
		# (if small-amount offers are gone)
		#
		for offer_price, offer_base in offers:
			claimed_base = worse_quote / offer_price

			# not enough base available, skip
			if claimed_base > offer_base:
				continue

			# all wanted base can be bought
			if claimed_base <= offer_base:
				transactions[-1]['worse_result_base'] = claimed_base
				break

		return transactions

	def simulate_sell_transactions(self, base:float, offers:list, fee_percent = 0.0, worse_base:float = None):
		offers = [v for v in sorted(offers, key=lambda v: v[0], reverse=True)]
		base = base * (1 - fee_percent / 100)
		quote = 0.0
		worse_base = worse_base * (1 - fee_percent / 100)

		transactions = []
		transactions.append({
			'type': 'initial',
			'change_base': 0.0,
			'change_quote': 0.0,
			'result_base': base,
			'result_quote': 0.0,
			'worse_result_base': worse_base,
		})

		#
		# Ideal sell
		# (use all expensive offers)
		#
		for offer_price, offer_base in offers:

			# not enough base available, buy what you can
			if base > offer_base:
				base -= offer_base
				quote += offer_base * offer_price

				transactions.append({
					'type': 'sell',
					'price': offer_price,
					'available_amount': offer_base,
					'change_base': -1 * offer_base,
					'change_quote': offer_base * offer_price,
					'result_base': base,
					'result_quote': quote,
					'worse_result_quote': 0.0,
				})

			# all wanted base can be bought
			if base <= offer_base:
				change_quote = base * offer_price
				quote += change_quote
				base = 0.0

				transactions.append({
					'type': 'sell',
					'price': offer_price,
					'available_amount': offer_base,
					'change_base': -1 * base,
					'change_quote': change_quote,
					'result_base': base,
					'result_quote': quote,
					'worse_result_quote': 0.0,
				})

			# no base left, finish
			if base == 0:
				break

		#
		# Worse sell
		# (if small-amount offers are gone)
		#
		for offer_price, offer_base in offers:

			# not enough base available, skip
			if worse_base > offer_base:
				continue

			# all wanted base can be bought
			if worse_base <= offer_base:
				transactions[-1]['worse_result_quote'] = worse_base * offer_price
				break

		return transactions

