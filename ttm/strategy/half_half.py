import ccxt
from datetime import datetime
from ttm.strategy import Strategy
import re
from pprint import pprint

"""
(This file is part of TTM package)

TTM - ToTheMoon crypto trading bot

@author  Michal Mikolas (nanuqcz@gmail.com)
"""
class HalfHalf(Strategy):

	def __init__(self, pair: str, minimal_move=5.0, tick_period=60, timeframe='1m', ext_balances={}):
		super().__init__()

		# Config
		self.pair = pair
		self.minimal_move = minimal_move    # percent
		self.tick_period = tick_period      # seconds
		self.timeframe = timeframe
		self.ext_balances = ext_balances

		# Internal
		self.error_sent = False

	def start(self):
		(self.symbol1, self.symbol2) = self.bot.split_pair(self.pair)

	def tick(self):
		ohlcv = self.bot.get_ohlcvs(self.pair, self.timeframe)[-1]
		price = ohlcv[4]

		balance1 = self.get_balance(self.symbol1)
		balance2 = self.get_balance(self.symbol2)
		value2 = balance2 / price

		move = (value2 - balance1) / value2 * 100  # percent
		if abs(move) < self.minimal_move:
			return

		target_balance1 = (balance1 + value2) / 2
		target_change = target_balance1 - balance1

		if target_change > 0:
			buy_amount = target_balance1 - balance1
			self.bot.log(
				"Buying {:f}. Reason: balance1={:f}, balance2={:f}, value2={:f}, move={:f}, self.minimal_move={:f}".format(
					buy_amount, balance1, balance2, value2, move, self.minimal_move
				),
				priority=1,
				extra_values=False
			)

			self.buy(self.pair, buy_amount, price)

		if target_change < 0:
			sell_amount = balance1 - target_balance1
			self.bot.log(
				"Selling {:f}. Reason: balance1={:f}, balance2={:f}, value2={:f}, move={:f}, self.minimal_move={:f}".format(
					sell_amount, balance1, balance2, value2, move, self.minimal_move
				),
				priority=1,
				extra_values=False
			)

			self.sell(self.pair, sell_amount, price)

	def get_balance(self, symbol):
		balance = self.bot.get_balance(symbol)

		if symbol in self.ext_balances:
			balance += self.ext_balances[symbol]

		return balance

	def command(self, chatbot, command: str, args=[]):
		command = command.lower()

		# # TargetValue
		# if command in ['target', 'targetvalue', 'target-value', 'target_value']:
		# 	# Save new value
		# 	if len(args) >= 1:
		# 		if re.match(r'^[0-9.]+$', args[0]):
		# 			self.save_target_value(args[0])

		# 		else:
		# 			chatbot.send_message(
		# 				'Error: Value "`{:s}`" is not valid number.'.format(args[0])
		# 			)

		# 	# Send current value
		# 	chatbot.send_message(
		# 		'*Target value:* {:5.5f}'.format(self.get_target_value())
		# 	)

		# # Unsupported
		# else:
		# 	chatbot.send_message('Unsupported command "`{:s}`".'.format(command))


	################################################################################

	def buy(self, pair, amount, price):
		try:
			self.bot.log(
				"/half_half/buy: Buying %f of %s for price %f" % (amount, pair, price),
				priority=1,
				extra_values=False
			)
			self.bot.buy(pair, amount, price)
			self.bot.log(
				"/half_half/buy: Buy order sent.",
				priority=1,
				extra_values=False
			)

			self.error_sent = False
			self.bot.log(
				"/half_half/buy: returning True.",
				priority=1,
				extra_values=False
			)
			return True

		except ccxt.InvalidOrder as e:
			self.bot.log(
				'Buy of {:5.5f} {:s} failed.'.format(amount, self.symbol1),
				priority=(1 if self.error_sent else 2)
			)
			self.bot.log(
				e,
				priority=(1 if self.error_sent else 2),
				extra_values=False
			)
			self.error_sent = True

	def sell(self, pair, amount, price):
		try:
			self.bot.log(
				"/half_half/sell: Selling %f of %s for price %f" % (amount, pair, price),
				priority=1,
				extra_values=False
			)
			self.bot.sell(pair, amount, price)
			self.bot.log(
				"/half_half/sell: Sell order sent.",
				priority=1,
				extra_values=False
			)

			self.error_sent = False
			self.bot.log(
				"/half_half/sell: returning True.",
				priority=1,
				extra_values=False
			)
			return True

		except ccxt.InvalidOrder as e:
			self.bot.log(
				'Sell of {:5.5f} {:s} failed...'.format(amount, self.symbol1),
				priority=(1 if self.error_sent else 2)
			)
			self.bot.log(
				e,
				priority=(1 if self.error_sent else 2),
				extra_values=False
			)
			self.error_sent = True
