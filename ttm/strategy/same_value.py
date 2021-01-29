import ccxt
from datetime import datetime
from ttm.strategy import Strategy

"""
(This file is part of TTM package)

TTM - ToTheMoon crypto trading bot

@author  Michal Mikolas (nanuqcz@gmail.com)
"""
class SameValue(Strategy):

	def __init__(self, pair: str, initial_target_value: float, minimal_move=5.0, tick_period=60, timeframe='1m', sell_modifier=1.00, buy_modifier=1.00):
		super().__init__()

		# Config
		self.pair = pair
		self.initial_target_value = initial_target_value
		self.minimal_move = minimal_move    # percent
		self.tick_period = tick_period      # seconds
		self.timeframe = timeframe
		self.sell_modifier = sell_modifier  # percent
		self.buy_modifier = buy_modifier    # percent

		# Internal
		self.error_sent = False

	def start(self):
		(self.currency1, self.currency2) = self.bot.split_pair(self.pair)

	def tick(self):
		ohlcv = self.bot.get_ohlcvs(self.pair, self.timeframe)[-1]
		balance = self.bot.get_balance(self.currency1)

		target_balance = self.get_target_value() / ohlcv[4]
		move = (balance - target_balance) / target_balance * 100  # percent

		if move >= self.minimal_move:
			sell_amount = (balance - target_balance) * self.sell_modifier

			if self.sell(self.pair, sell_amount, ohlcv[4]):
				self.save_target_value((balance - sell_amount) * ohlcv[4])

		elif move <= -1*self.minimal_move:
			buy_amount = (target_balance - balance) * self.buy_modifier

			if self.buy(self.pair, buy_amount, ohlcv[4]):
				self.save_target_value((balance + buy_amount) * ohlcv[4])

	################################################################################

	def buy(self, pair, amount, price):
		try:
			self.bot.buy(pair, amount, price)

			self.error_sent = False
			return True

		except ccxt.InvalidOrder as e:
			self.bot.log(
				'Buy of {:5.5f} {:s} failed.'.format(amount, self.currency1),
				priority=(0 if self.error_sent else 2)
			)
			self.bot.log(
				e,
				priority=(0 if self.error_sent else 2),
				extra_values=False
			)
			self.error_sent = True

	def sell(self, pair, amount, price):
		try:
			self.bot.sell(pair, amount, price)

			self.error_sent = False
			return True

		except ccxt.InvalidOrder as e:
			self.bot.log(
				'Sell of {:5.5f} {:s} failed...'.format(amount, self.currency1),
				priority=(0 if self.error_sent else 2)
			)
			self.bot.log(
				e,
				priority=(0 if self.error_sent else 2),
				extra_values=False
			)
			self.error_sent = True

	def get_target_value(self):
		target_value = self.bot.storage.get('target_value')

		if not target_value:
			target_value = self.initial_target_value
			self.bot.storage.save('target_value', target_value)

		return target_value

	def save_target_value(self, target_value):
		self.bot.storage.save('target_value', target_value)
