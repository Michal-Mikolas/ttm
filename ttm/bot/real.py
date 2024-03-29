import ccxt
from ccxt import Exchange
from ttm.bot import Bot
from ttm.strategy import Strategy
from ttm.storage import Storage
from ttm.logger import Logger
from datetime import datetime
from dateutil.parser import parse
import time
from urllib3.exceptions import ProtocolError


"""
(This file is part of TTM package)

TTM - ToTheMoon crypto trading bot

@author  Michal Mikolas (nanuqcz@gmail.com)
"""
class Real(Bot):

	###
	 #  #    # # #####
	 #  ##   # #   #
	 #  # #  # #   #
	 #  #  # # #   #
	 #  #   ## #   #
	### #    # #   #

	def __init__(self, exchange: Exchange, strategy: Strategy, storage: Storage, cache: Storage, logger: Logger):
		super().__init__(exchange, strategy, storage, cache, logger)

		self.chatbot = None
		self.status = 'active'

	def set_chatbot(self, chatbot):
		self.chatbot = chatbot
		self.chatbot.set_bot(self)

	#######
	#     # #####  #####  ###### #####   ####
	#     # #    # #    # #      #    # #
	#     # #    # #    # #####  #    #  ####
	#     # #####  #    # #      #####       #
	#     # #   #  #    # #      #   #  #    #
	####### #    # #####  ###### #    #  ####

	def buy(self, pair: str, amount: float = None, price: float = None, cost: float = None):
		if amount and price:
			return self.buy_limit(pair, amount, price)

		if cost:
			return self.buy_market(pair, amount=amount, cost=cost)

		raise Exception("Can't place buy order with given parameters.")

	def buy_limit(self, pair: str, amount: float, price: float):
		self.exchange.create_order(pair, 'limit', 'buy', amount, price)

		symbols = self.split_pair(pair)
		self.log(
			'Buy order of {:f} {:s} created (limit)'.format(amount, symbols[0]),
			priority=2
		)

	def buy_market(self, pair: str, amount: float = None, cost: float = None):
		if amount and not cost:
			self.exchange.create_market_buy_order(pair, amount=amount)

			symbols = self.split_pair(pair)
			self.log(
				'Buy order of {:f} {:s} for {:s} created (market)'.format(cost, symbols[0], symbols[1]),
				priority=2
			)

		if cost and not amount:
			self.exchange.options['createMarketBuyOrderRequiresPrice'] = False

			self.exchange.create_market_buy_order(pair, cost)

			symbols = self.split_pair(pair)
			self.log(
				'Buy order of {:s} for {:f} {:s} created (market)'.format(symbols[0], cost, symbols[1]),
				priority=2
			)

			return

		raise Exception("Can't place market buy order with given parameters.")

	def sell(self, pair, amount, price: float = None):
		if amount and price:
			return self.sell_limit(pair, amount, price)

		if amount and not price:
			return self.sell_market(pair, amount)

		raise Exception("Can't place sell order with given parameters.")

	def sell_limit(self, pair: str, amount: float, price: float):
		self.exchange.create_order(pair, 'limit', 'sell', amount, price)

		symbols = self.split_pair(pair)
		self.log(
			'Sell order of {:f} {:s} created'.format(amount, symbols[0]),
			priority=2
		)

	def sell_market(self, pair: str, amount: float):
		self.exchange.create_market_sell_order(pair, amount)

		symbols = self.split_pair(pair)
		self.log(
			'Sell order of {:f} {:s} created (market)'.format(amount, symbols[0]),
			priority=2
		)

	def get_open_orders(self, symbol: str, since=None, limit=None):
		since = self._to_exchange_timestamp(since)

		return self.exchange.fetchOpenOrders(symbol, since, limit)

	def cancel_order(self, order):
		return self.exchange.cancel_order(order['id'], order['symbol'])

	 #####
	#     # #    # #####  #####  ###### #    #  ####  # ######  ####
	#       #    # #    # #    # #      ##   # #    # # #      #
	#       #    # #    # #    # #####  # #  # #      # #####   ####
	#       #    # #####  #####  #      #  # # #      # #           #
	#     # #    # #   #  #   #  #      #   ## #    # # #      #    #
	 #####   ####  #    # #    # ###### #    #  ####  # ######  ####

	def get_balance(self, symbol):
		# Fetch data from exchange
		balances = self.exchange.fetch_free_balance()

		# Return
		if symbol in balances:
			return balances[symbol]
		else:
			return 0.0

	def get_tickers(self, pairs):
		return self.exchange.fetch_tickers(pairs)

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

	######
	#     # #    # #    #
	#     # #    # ##   #
	######  #    # # #  #
	#   #   #    # #  # #
	#    #  #    # #   ##
	#     #  ####  #    #

	def run(self):
		self.log('Starting bot...', priority=1)
		self.strategy.start()

		while True:
			try:
				if self.status == 'active':
					self.log('tick...', priority=0)
					self.strategy.tick()

			except (ccxt.RequestTimeout, ccxt.NetworkError, ProtocolError) as e:
				try:
					self.log_exception(e)
					exception_message = "network error... %s: %s" % (type(e).__name__, str(e)[0:255])
					self.log(exception_message, priority=0, extra_values=False)
				except Exception as e:
					self.log_exception(e)

			finally:
				try:
					self.log(
						'waiting {:d} seconds...'.format(self.strategy.tick_period),
						priority=0,
						extra_values=False
					)
				except Exception as e:
					self.log_exception(e)

				time.sleep(self.strategy.tick_period)

	def __del__(self):
		self.log('Terminating bot...', priority=1)
		self.strategy.finish()
