from ccxt import Exchange
from ttm.strategy.strategy import Strategy
from datetime import datetime
from dateutil.parser import parse

"""
TTM - ToTheMoon crypto trading bot

@author  Michal Mikolas (nanuqcz@gmail.com)
"""
class Bot():

	def __init__(self, exchange: Exchange, strategy: Strategy):
		self.exchange = exchange

		self.strategy = strategy
		self.strategy.set_bot(self)

		self.mode = 'backtest'  # backtest|real
		self.cache = {}

		# backtesting
		self.now = datetime.now()
		self.backtest_from = None
		self.backtest_to = None

	def buy(self, pair, amount):
		pass

	def sell(self, pair, amount):
		pass

	def get_balance(self, pair):
		pass

	def storage(self, key, value):
		pass

	def get_ohlcvs(self, pair, type, from_datetime=None, till_datetime=None):
		from_timestamp = self.exchange.parse8601(from_datetime) if from_datetime else None
		till_timestamp = self.exchange.parse8601(till_datetime) if till_datetime else None

		if self.mode == 'backtest':
			# TODO Cache whole backtest period ...
			cache_key = pair + '-' + type
			if cache_key not in self.cache:
				self.cache[cache_key] = self._download_ohlcvs(
					pair,
					type,
					self._to_exchange_timestamp(self.backtest_from) - self.strategy.backtest_history_need.get(cache_key, 0) * 1000,  # exchange timestamp is in miliseconds
					self._to_exchange_timestamp(self.backtest_to)
				)

			# TODO ...and then load everything from cache
			ohlcvs = [x for x in self.cache[cache_key] if x[0] >= from_timestamp and x[0] <= till_timestamp]

		if self.mode == 'real':
			ohlcvs = self._download_ohlcvs(pair, type, from_timestamp, till_timestamp)

		return ohlcvs

	def _download_ohlcvs(self, pair, type, from_timestamp=None, till_timestamp=None):
		# TODO pagination: https://github.com/ccxt/ccxt/blob/master/examples/py/poloniex-fetch-ohlcv-with-pagination.py
		ohlcvs = self.exchange.fetch_ohlcv(pair, type, from_timestamp, till_timestamp)

		# fix for exchanges that returns more data then asked
		ohlcvs = [x for x in ohlcvs if x[0] >= from_timestamp and x[0] <= till_timestamp]

		return ohlcvs

	def _to_exchange_timestamp(self, date=None):
		if type(date) is str:
			return self.exchange.parse8601(date)

		if type(date) is int:
			return date

		if type(date) is datetime:
			return self.exchange.parse8601(date.isoformat())  # let ccxt handle timezone

		return None


	#######
	   #    #####    ##   #####  # #    #  ####
	   #    #    #  #  #  #    # # ##   # #    #
	   #    #    # #    # #    # # # #  # #
	   #    #####  ###### #    # # #  # # #  ###
	   #    #   #  #    # #    # # #   ## #    #
	   #    #    # #    # #####  # #    #  ####

	def run_real(self):
		self.mode = 'real'

	######
	#     #   ##    ####  #    # ##### ######  ####  #####
	#     #  #  #  #    # #   #    #   #      #        #
	######  #    # #      ####     #   #####   ####    #
	#     # ###### #      #  #     #   #           #   #
	#     # #    # #    # #   #    #   #      #    #   #
	######  #    #  ####  #    #   #   ######  ####    #

	def run_backtest(self, date_from: str, date_to: str):
		#
		# 1) Init
		#
		self.mode = 'backtest'
		self.backtest_from = parse(date_from)
		self.backtest_to = parse(date_to)
		self.now = self.backtest_from

		#
		# 2) Run simulation
		#
		tick = datetime.timedelta(seconds=self.strategy.tick_period)
		while True:
			self.strategy.tick()
			self.now = self.now + tick

			if self.now > self.backtest_to:
				break

