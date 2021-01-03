from ccxt import Exchange
from ttm.bot import Bot
from ttm.strategy import Strategy
from ttm.storage import Storage
from ttm.logger import Logger
from ttm.statistics import Real as RealStatistics
from datetime import datetime, timedelta
from dateutil.parser import parse

"""
(This file is part of TTM package)

TTM - ToTheMoon crypto trading bot

@author  Michal Mikolas (nanuqcz@gmail.com)
"""
class Backtest(Bot):

	def __init__(self, exchange: Exchange, strategy: Strategy, storage: Storage, cache: Storage, logger: Logger,
		date_from: str, date_to: str, initial_balances = {}
	):
		super().__init__(exchange, strategy, storage, cache, logger)

		# backtesting
		self.backtest_from = parse(date_from)
		self.backtest_now = self.backtest_from
		self.backtest_to = parse(date_to)
		self.backtest_balances = initial_balances

		self.statistics = RealStatistics()  # for backtesting, turn on statistics module

	def buy(self, pair: str, amount: float, price: float):
		# 1) Calculate new balances
		currencies = self.split_pair(pair)
		balance1 = self.get_balance(currencies[0])
		balance2 = self.get_balance(currencies[1])

		balance1 += amount
		balance2 -= amount * price

		# 2) Calculate fees
		fee = self._calculate_fee(pair, 'limit', 'buy', amount, price)
		balance2 -= fee['cost']

		# 3) Save new balances
		self.backtest_balances[currencies[0]] = balance1
		self.backtest_balances[currencies[1]] = balance2

		# 4) Finish
		self.log('Bought {:f} {:s}'.format(amount, currencies[0]))

	def sell(self, pair: str, amount: float, price: float):
		# 1) Calculate new balances
		currencies = self.split_pair(pair)
		balance1 = self.get_balance(currencies[0])
		balance2 = self.get_balance(currencies[1])

		balance1 -= amount
		balance2 += amount * price

		# 2) Calculate fees
		fee = self._calculate_fee(pair, 'limit', 'sell', amount, price)
		balance2 -= fee['cost']

		# 3) Save new balances
		self.backtest_balances[currencies[0]] = balance1
		self.backtest_balances[currencies[1]] = balance2

		# 4) Finish
		self.log('Sold {:f} {:s}'.format(amount, currencies[0]))

	def get_balance(self, symbol):
		if symbol not in self.backtest_balances:
			self.backtest_balances[symbol] = 0.0

		return self.backtest_balances[symbol]

	def get_ohlcvs(self, pair: str, timeframe: str = None, from_datetime=None, till_datetime=None):
		# Prepare
		timeframe = timeframe if timeframe else self._get_last_timeframe()
		if not timeframe:
			return None

		from_timestamp = self.exchange.parse8601(from_datetime) if from_datetime else None
		till_timestamp = self.exchange.parse8601(till_datetime) if till_datetime else self._to_exchange_timestamp(self.backtest_now)

		# Save whole backtest period ...
		temp_key = pair + '-' + timeframe
		if temp_key not in self.temp:
			self.temp[temp_key] = self._download_ohlcvs(
				pair,
				timeframe,
				self._to_exchange_timestamp(self.backtest_from) - self.strategy.backtest_history_need.get(temp_key, 0) * 1000,  # exchange timestamp is in miliseconds
				self._to_exchange_timestamp(self.backtest_to)
			)

		# ...and then load everything from temp
		ohlcvs = [x for x in self.temp[temp_key] if x[0] <= till_timestamp]
		if from_timestamp:
			ohlcvs = [x for x in ohlcvs if x[0] >= from_timestamp]

		# Finish
		return ohlcvs

	def run(self):
		#
		# 1) Init
		#
		self.backtest_now = self.backtest_from
		self.log('Starting')

		#
		# 2) Run simulation
		#
		self.strategy.start()

		tick = timedelta(seconds=self.strategy.tick_period)
		while True:
			self.strategy.tick()
			self.backtest_now = self.backtest_now + tick

			if self.backtest_now > self.backtest_to:
				break

	def now(self):
		return self.backtest_now

	def __del__(self):
		self.log('Finishing')
		self.strategy.finish()
