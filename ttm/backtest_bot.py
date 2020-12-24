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

	def __init__(self, exchange: Exchange, strategy: Strategy, storage: Storage,
		date_from: str, date_to: str, initial_balances = {}
	):
		super().__init__(exchange, strategy, storage)

		# backtesting
		self.now = datetime.now()
		self.backtest_from = parse(date_from)
		self.backtest_to = parse(date_to)
		self.backtest_balances = initial_balances
		self.smallest_timeframe = None

	def buy(self, pair: str, amount: float, log_values = {}):
		# 1) Get pair price
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

	def sell(self, pair: str, amount: float, log_values={}):
		pass

	def get_balance(self, pair):
		if pair not in self.backtest_balances:
			self.backtest_balances[pair] = 0.0

		return self.backtest_balances[pair]

	def get_ohlcvs(self, pair, timefrime, from_datetime=None, till_datetime=None):
		from_timestamp = self.exchange.parse8601(from_datetime) if from_datetime else None
		till_timestamp = self.exchange.parse8601(till_datetime) if till_datetime else self._to_exchange_timestamp(self.now)

		# Cache whole backtest period ...
		cache_key = pair + '-' + timefrime
		if cache_key not in self.cache:
			self.cache[cache_key] = self._download_ohlcvs(
				pair,
				timefrime,
				self._to_exchange_timestamp(self.backtest_from) - self.strategy.backtest_history_need.get(cache_key, 0) * 1000,  # exchange timestamp is in miliseconds
				self._to_exchange_timestamp(self.backtest_to)
			)

		# ...and then load everything from cache
		ohlcvs = [x for x in self.cache[cache_key] if x[0] <= till_timestamp]
		if from_timestamp:
			ohlcvs = [x for x in ohlcvs if x[0] >= from_timestamp]

		return ohlcvs

	def run(self):
		#
		# 1) Init
		#
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
