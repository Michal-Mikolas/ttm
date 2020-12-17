import ccxt

"""
TTM - ToTheMoon crypto trading bot

@author  Michal Mikolas (nanuqcz@gmail.com)
"""
class Bot():

	def __init__(self, exchange, strategy):
		self.exchange = exchange
		self.strategy = strategy

	def run_trading(self):
		pass

	def run_backtest(self, date_from, date_to, timeframe):
		pass

	def get_candles(self, pair, type, limit=100):
		pass

	def buy(self, pair, amount):
		pass

	def sell(self, pair, amount):
		pass

	def get_wallet(self, pair):
		pass

	def storage(self, key, value):
		pass


