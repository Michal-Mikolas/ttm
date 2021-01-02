from ccxt import Exchange
from ttm.strategy import Strategy
from ttm.storage import Storage
from ttm.logger import Logger
from ttm.statistics import Fake as FakeStatistics
from datetime import datetime
from dateutil.parser import parse


"""
(This file is part of TTM package)

TTM - ToTheMoon crypto trading bot

@author  Michal Mikolas (nanuqcz@gmail.com)
"""
class Bot():

	def __init__(self, exchange: Exchange, strategy: Strategy, storage: Storage, cache: Storage, logger: Logger):
		self.exchange = exchange

		self.strategy = strategy
		self.strategy.set_bot(self)

		self.storage = storage
		self.cache = cache
		self.logger = logger

		self.temp = {}

		self.statistics = FakeStatistics()  # in real run, statistics are disabled because of performance

	def buy(self, pair, amount, price: float = None):
		pass

	def sell(self, pair, amount, price: float = None):
		pass

	def get_balance(self, symbol):
		pass

	def get_ohlcvs(self, pair, timeframe, from_datetime=None, till_datetime=None):
		pass

	def run(self):
		pass

	def log(self, *args):
		return self.logger.log(*args)

	###
	 #  #    # ##### ###### #####  #    #   ##   #
	 #  ##   #   #   #      #    # ##   #  #  #  #
	 #  # #  #   #   #####  #    # # #  # #    # #
	 #  #  # #   #   #      #####  #  # # ###### #
	 #  #   ##   #   #      #   #  #   ## #    # #
	### #    #   #   ###### #    # #    # #    # ######

	def _download_ohlcvs(self, pair, timeframe, from_timestamp: int = None, till_timestamp: int = None):
		all_ohlcvs = None

		# Try to load from cache
		cache_key = (pair + '-' + timeframe + '-' + str(from_timestamp) + '-' + str(till_timestamp)) if (from_timestamp and till_timestamp) else None
		if cache_key:
			all_ohlcvs = self.cache.get(cache_key)

		# Download from the server for the first time
		if not all_ohlcvs:
			ohlcv_duration = self.exchange.parse_timeframe(timeframe) * 1000

			all_ohlcvs = []
			page_start_timestamp = from_timestamp
			while True:
				ohlcvs = self.exchange.fetch_ohlcv(pair, timeframe, page_start_timestamp, till_timestamp)
				all_ohlcvs += ohlcvs

				page_start_timestamp = all_ohlcvs[-1][0] + ohlcv_duration

				if from_timestamp is None or till_timestamp is None or page_start_timestamp >= till_timestamp:
					break

			# fix for exchanges that returns more data then asked
			if from_timestamp:
				all_ohlcvs = [x for x in all_ohlcvs if x[0] >= from_timestamp]
			if till_timestamp:
				all_ohlcvs = [x for x in all_ohlcvs if x[0] <= till_timestamp]

			# Save results to cache if possible
			if cache_key:
				self.cache.save(cache_key, all_ohlcvs)

		return all_ohlcvs

	def _to_exchange_timestamp(self, date=None):
		if type(date) is str:
			return self.exchange.parse8601(date)

		if type(date) is int:
			return date

		if type(date) is datetime:
			return self.exchange.parse8601(date.isoformat())  # let ccxt handle timezone

		return None

	def _calculate_fee(self, symbol: str, type: str, side: str, amount: float, price: float, takerOrMaker: str = None, params={}):
		"""
		Original function:
		ccxt.exchange.calculate_fee(self, symbol, type, side, amount, price, takerOrMaker='taker', params={})

		...is not working. So after they fix the error, we can use it like this instead of my hotfix:
		exchange.calculate_fee('BTC/USD', 'limit', 'buy', 0.001, 10000)
		"""
		fee = {
			'rate': None,
			'type': takerOrMaker,
			'currency': symbol.split('/')[1],
			'cost': 0.0,
		}

		if not fee['type']:
			fee['type'] = 'taker' if type == 'buy' else 'maker'

		if self.exchange.fees['trading']['percentage']:
			fee['cost'] += price * amount * self.exchange.fees['trading'][fee['type']]

		if self.exchange.fees['trading']['tierBased']:
			raise Exception("'tierBased' fees are not implemented.")

		return fee
