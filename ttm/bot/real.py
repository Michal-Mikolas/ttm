from ccxt import Exchange
from ttm.bot import Bot
from ttm.strategy import Strategy
from ttm.storage import Storage
from ttm.logger import Logger
from datetime import datetime
from dateutil.parser import parse
import time


"""
(This file is part of TTM package)

TTM - ToTheMoon crypto trading bot

@author  Michal Mikolas (nanuqcz@gmail.com)
"""
class Real(Bot):

	def __init__(self, exchange: Exchange, strategy: Strategy, storage: Storage, cache: Storage, logger: Logger):
		super().__init__(exchange, strategy, storage, cache, logger)

	def buy(self, pair, amount, price: float):
		self.exchange.create_order(pair, 'limit', 'buy', amount, price)
		# if self.exchange.has['createMarketOrder']:
		# 	self.exchange.create_order(pair, 'market', 'buy', amount, price)
		# 	# alternative? exchange: 'options': 'create_market_buy_orderRequiresPrice': false}
		# 	# self.exchange.create_market_buy_order(pair, price * amount)
		# else:
		# 	self.exchange.create_order(pair, 'limit', 'buy', amount, price)
		# 	# self.exchange.create_limit_buy_order(pair, amount, price)

	def sell(self, pair, amount, price: float):
		self.exchange.create_order(pair, 'limit', 'sell', amount, price)

	def get_balance(self, symbol):
		balances = self.exchange.fetch_free_balance()

		if symbol in balances:
			return balances[symbol]
		else:
			return 0.0

	def get_ohlcvs(self, pair, timeframe: str = None, from_datetime=None, till_datetime=None):
		# Prepare
		timeframe = timeframe if timeframe else self._get_last_timeframe()
		if not timeframe:
			return None

		from_timestamp = self.exchange.parse8601(from_datetime) if from_datetime else None
		till_timestamp = self.exchange.parse8601(till_datetime) if till_datetime else None

		# Fetch candles
		ohlcvs = self._download_ohlcvs(pair, timeframe, from_timestamp, till_timestamp)

		# Finish
		return ohlcvs

	def run(self):
		self.strategy.start()

		while True:
			self.strategy.tick()

			time.sleep(self.strategy.tick_period)

	def __del__(self):
		self.strategy.finish()

	def _download_ohlcvs(self, pair: str, timeframe: str, from_timestamp: int = None, till_timestamp: int = None):
		if from_timestamp or till_timestamp:
			ohlcvs = super()._download_ohlcvs(pair, timeframe, from_timestamp, till_timestamp)
		else:
			ohlcvs = self._download_last_ohlcvs(pair, timeframe)

		return ohlcvs

	def _download_last_ohlcvs(self, pair: str, timeframe: str):
		ohlcvs = None
		cache_key = "%s-%s" % (pair, timeframe)

		# Try to load from cache
		if cache_key in self.temp:
			# Cache lasts for 2 seconds
			if (datetime.now() - self.temp[cache_key]['created']).total_seconds() <= 2:
				ohlcvs = self.temp[cache_key]['ohlcvs']

		# If not in cache, download & cache
		if not ohlcvs:
			ohlcvs = super()._download_ohlcvs(pair, timeframe)

			self.temp[cache_key] = {
				'created': datetime.now(),
				'ohlcvs': ohlcvs,
			}

		# Finish
		return ohlcvs
