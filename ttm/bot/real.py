from ccxt import Exchange
from ttm.bot import Bot
from ttm.strategy import Strategy
from ttm.storage import Storage
from ttm.logger import Logger
from ttm.statistics import Fake as FakeStatistics
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

	def buy(self, pair, amount, price: float = None):
		# 1) Get pair price
		if not price:
			ohlcvs = self.get_ohlcvs(pair, self.get_smallest_timeframe())
			price = ohlcvs[-1][4]

		# 2) Create order
		self.exchange.create_order(pair, 'limit', 'buy', amount, price)
		# if self.exchange.has['createMarketOrder']:
		# 	self.exchange.create_order(pair, 'market', 'buy', amount, price)
		# 	# alternative? exchange: 'options': 'create_market_buy_orderRequiresPrice': false}
		# 	# self.exchange.create_market_buy_order(pair, price * amount)
		# else:
		# 	self.exchange.create_order(pair, 'limit', 'buy', amount, price)
		# 	# self.exchange.create_limit_buy_order(pair, amount, price)

	def sell(self, pair, amount, price: float = None):
		# 1) Get pair price
		if not price:
			ohlcvs = self.get_ohlcvs(pair, self.get_smallest_timeframe())
			price = ohlcvs[-1][4]

		# 2) Create order
		self.exchange.create_order(pair, 'limit', 'sell', amount, price)

	def get_balance(self, symbol):
		balances = self.exchange.fetch_free_balance()

		if symbol in balances:
			return balances[symbol]
		else:
			return 0.0

	def get_ohlcvs(self, pair, timeframe, from_datetime=None, till_datetime=None):
		# Prepare
		from_timestamp = self.exchange.parse8601(from_datetime) if from_datetime else None
		till_timestamp = self.exchange.parse8601(till_datetime) if till_datetime else self._to_exchange_timestamp(self.now)

		# Fetch candles
		ohlcvs = self._download_ohlcvs(pair,timeframe,from_timestamp,till_timestamp)

		# Finish
		return ohlcvs

	def run(self):
		self.strategy.start()

		while True:
			self.strategy.tick()

			time.wait(self.strategy.tick_period)

	def __del__(self):
		self.strategy.finish()

	def log(self, *args):
		return self.logger.log(*args)
