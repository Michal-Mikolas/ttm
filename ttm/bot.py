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

	def get_ohlcvs(self, pair, timefrime, from_datetime=None, till_datetime=None):
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

	def _download_ohlcvs(self, pair, timefrime, from_timestamp=None, till_timestamp=None):
		duration = self.exchange.parse_timeframe(timefrime) * 1000

		all_ohlcvs = []
		page_start_timestamp = from_timestamp
		while page_start_timestamp < till_timestamp:
			ohlcvs = self.exchange.fetch_ohlcv(pair, timefrime, page_start_timestamp, till_timestamp)
			all_ohlcvs += ohlcvs

			page_start_timestamp = all_ohlcvs[-1][0] + duration

		# fix for exchanges that returns more data then asked
		all_ohlcvs = [x for x in all_ohlcvs if x[0] >= from_timestamp and x[0] <= till_timestamp]

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
