from ccxt import Exchange
from ttm.strategy import Strategy
from ttm.storage import Storage
from datetime import datetime
from dateutil.parser import parse

"""
TTM - ToTheMoon crypto trading bot

@author  Michal Mikolas (nanuqcz@gmail.com)
"""
class Bot():

	def __init__(self, exchange: Exchange, strategy: Strategy, storage: Storage):
		self.exchange = exchange

		self.strategy = strategy
		self.strategy.set_bot(self)

		self.storage = storage

		self.cache = {}

	def buy(self, pair, amount):
		pass

	def sell(self, pair, amount):
		pass

	def get_balance(self, pair):
		pass

	def get_ohlcvs(self, pair, type, from_datetime=None, till_datetime=None):
		pass

	def run(self):
		pass

	###
	 #  #    # ##### ###### #####  #    #   ##   #
	 #  ##   #   #   #      #    # ##   #  #  #  #
	 #  # #  #   #   #####  #    # # #  # #    # #
	 #  #  # #   #   #      #####  #  # # ###### #
	 #  #   ##   #   #      #   #  #   ## #    # #
	### #    #   #   ###### #    # #    # #    # ######

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

