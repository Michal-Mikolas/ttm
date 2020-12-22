from ccxt import Exchange
from ttm import Bot
from ttm.strategy import Strategy
from ttm.storage import Storage
from datetime import datetime
from dateutil.parser import parse

"""
TTM - ToTheMoon crypto trading bot

@author  Michal Mikolas (nanuqcz@gmail.com)
"""
class BacktestBot(Bot):

	def __init__(self, exchange: Exchange, strategy: Strategy, storage: Storage):
		super().__init__(exchange, strategy, storage)

		# backtesting
		self.now = datetime.now()
		self.backtest_from = None
		self.backtest_to = None
		self.backtest_balances = {}

	def buy(self, pair, amount):
		# 1) Get pair price
		# 2) Save new balances
		# 3) Calculate fees
		pass

	def sell(self, pair, amount):
		pass

	def get_balance(self, pair):
		if pair not in self.backtest_balances:
			self.backtest_balances[pair] = 0.0

		return self.backtest_balances[pair]

	def get_ohlcvs(self, pair, type, from_datetime=None, till_datetime=None):
		from_timestamp = self.exchange.parse8601(from_datetime) if from_datetime else None
		till_timestamp = self.exchange.parse8601(till_datetime) if till_datetime else None

		# Cache whole backtest period ...
		cache_key = pair + '-' + type
		if cache_key not in self.cache:
			self.cache[cache_key] = self._download_ohlcvs(
				pair,
				type,
				self._to_exchange_timestamp(self.backtest_from) - self.strategy.backtest_history_need.get(cache_key, 0) * 1000,  # exchange timestamp is in miliseconds
				self._to_exchange_timestamp(self.backtest_to)
			)

		# ...and then load everything from cache
		ohlcvs = [x for x in self.cache[cache_key] if x[0] >= from_timestamp and x[0] <= till_timestamp]

		return ohlcvs

	def run(self, date_from: str, date_to: str):
		#
		# 1) Init
		#
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

