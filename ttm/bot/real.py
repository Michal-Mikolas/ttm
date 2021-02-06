import ccxt
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

		self.chatbot = None
		self.status = 'active'

	def set_chatbot(self, chatbot):
		self.chatbot = chatbot
		self.chatbot.set_bot(self)

	def buy(self, pair, amount, price: float):
		self.exchange.create_order(pair, 'limit', 'buy', amount, price)

		currencies = self.split_pair(pair)
		self.log(
			'Bought {:f} {:s}'.format(amount, currencies[0]),
			priority=2
		)

		# if self.exchange.has['createMarketOrder']:
		# 	self.exchange.create_order(pair, 'market', 'buy', amount, price)
		# 	# alternative? exchange: 'options': 'create_market_buy_orderRequiresPrice': false}
		# 	# self.exchange.create_market_buy_order(pair, price * amount)
		# else:
		# 	self.exchange.create_order(pair, 'limit', 'buy', amount, price)
		# 	# self.exchange.create_limit_buy_order(pair, amount, price)

	def sell(self, pair, amount, price: float):
		self.exchange.create_order(pair, 'limit', 'sell', amount, price)

		currencies = self.split_pair(pair)
		self.log(
			'Sold {:f} {:s}'.format(amount, currencies[0]),
			priority=2
		)

	def get_balance(self, symbol):
		# Fetch data from exchange
		try:
			balances = self.exchange.fetch_free_balance()
		except:
			balances = {}

		# Return
		if symbol in balances:
			return balances[symbol]
		else:
			return 0.0

	def get_ohlcvs(self, pair: str = None, timeframe: str = None, from_datetime=None, till_datetime=None):
		# Prepare
		pair = pair if pair else self.get_last_pair()
		if not pair:
			return None

		timeframe = timeframe if timeframe else self.get_last_timeframe()
		if not timeframe:
			return None

		from_timestamp = self.exchange.parse8601(from_datetime) if from_datetime else None
		till_timestamp = self.exchange.parse8601(till_datetime) if till_datetime else None

		# Fetch candles
		ohlcvs = self._download_ohlcvs(pair, timeframe, from_timestamp, till_timestamp)

		# Finish
		return ohlcvs

	def run(self):
		self.log('Starting bot...', priority=1)
		self.strategy.start()

		while True:
			try:
				if self.status == 'active':
					self.log('tick...', priority=0)
					self.strategy.tick()

			except (ccxt.RequestTimeout, ccxt.NetworkError):
				self.log('network error...', priority=0, extra_values=False)

			finally:
				self.log(
					'waiting {:d} seconds...'.format(self.strategy.tick_period),
					priority=0,
					extra_values=False
				)
				time.sleep(self.strategy.tick_period)

	def __del__(self):
		self.log('Terminating bot...', priority=1)
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
			# Cache lasts for 30 seconds
			if (datetime.now() - self.temp[cache_key]['created']).total_seconds() <= 30:
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
