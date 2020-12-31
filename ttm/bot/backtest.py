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
		self.now = datetime.now()
		self.backtest_from = parse(date_from)
		self.backtest_to = parse(date_to)
		self.backtest_balances = initial_balances
		self.smallest_timeframe = None

		self.statistics = RealStatistics()  # for backtesting, turn on statistics module

	def buy(self, pair: str, amount: float, price: float = None):
		# 1) Get pair price
		if not price:
			ohlcvs = self.get_ohlcvs(pair, self.get_smallest_timeframe())
			price = ohlcvs[-1][4]

		# 2) Calculate new balances
		currencies = pair.split('/')
		balance1 = self.get_balance(currencies[0])
		balance2 = self.get_balance(currencies[1])

		balance1 += amount
		balance2 -= amount * price

		# 3) Calculate fees
		fee = self._calculate_fee(pair, 'limit', 'buy', amount, price)
		balance2 -= fee['cost']

		# 4) Save new balances
		self.backtest_balances[currencies[0]] = balance1
		self.backtest_balances[currencies[1]] = balance2

	def sell(self, pair: str, amount: float, price: float = None):
		# 1) Get pair price
		if not price:
			ohlcvs = self.get_ohlcvs(pair, self.get_smallest_timeframe())
			price = ohlcvs[-1][4]

		# 2) Calculate new balances
		currencies = pair.split('/')
		balance1 = self.get_balance(currencies[0])
		balance2 = self.get_balance(currencies[1])

		balance1 -= amount
		balance2 += amount * price

		# 3) Calculate fees
		fee = self._calculate_fee(pair, 'limit', 'sell', amount, price)
		balance2 -= fee['cost']

		# 4) Save new balances
		self.backtest_balances[currencies[0]] = balance1
		self.backtest_balances[currencies[1]] = balance2

	def get_balance(self, symbol):
		if symbol not in self.backtest_balances:
			self.backtest_balances[symbol] = 0.0

		return self.backtest_balances[symbol]

	def get_ohlcvs(self, pair: str, timeframe: str, from_datetime=None, till_datetime=None):
		from_timestamp = self.exchange.parse8601(from_datetime) if from_datetime else None
		till_timestamp = self.exchange.parse8601(till_datetime) if till_datetime else self._to_exchange_timestamp(self.now)

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
		self.update_smallest_timeframe(timeframe)
		return ohlcvs

	def run(self):
		#
		# 1) Init
		#
		self.now = self.backtest_from

		#
		# 2) Run simulation
		#
		self.strategy.start()

		tick = timedelta(seconds=self.strategy.tick_period)
		while True:
			self.strategy.tick()
			self.now = self.now + tick

			if self.now > self.backtest_to:
				break

	def __del__(self):
		self.strategy.finish()

	def get_smallest_timeframe(self):
		frames = {
			3*60: '3m',
			5*60: '5m',
			15*60: '15m',
			30*60: '30m',
			1*60*60: '1h',
			2*60*60: '2h',
			3*60*60: '3h',
			4*60*60: '4h',
			6*60*60: '6h',
			8*60*60: '8h',
			12*60*60: '12h',
			1*24*60*60: '1d',
			3*24*60*60: '3d',
			7*24*60*60: '1w',
			14*24*60*60: '2w',
			30*24*60*60: '1M',
			365*24*60*60: '1y',
		}

		if self.smallest_timeframe in frames:
			return frames[self.smallest_timeframe]
		else:
			return '1m'

	def update_smallest_timeframe(self, timeframe):
		seconds = self.exchange.parse_timeframe(timeframe)
		self.smallest_timeframe = seconds if (self.smallest_timeframe is None or seconds < self.smallest_timeframe) else self.smallest_timeframe
