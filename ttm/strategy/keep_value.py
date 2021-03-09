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
class KeepValue(Strategy):

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
			self.bot.log(
				"Selling {:f}. Reason: balance={:f}, target_balance={:f}, move={:f}, self.minimal_move={:f}".format(
					sell_amount, balance, target_balance, move, self.minimal_move
				),
				priority=1,
				extra_values=False
			)

			if self.sell(self.pair, sell_amount, ohlcv[4]):
				pprint(balance)
				pprint(sell_amount)
				pprint(ohlcv)
				self.bot.log(
					"Selling done. Setting target_value = %f" % ((balance - sell_amount) * ohlcv[4]),
					priority=1,
					extra_values=False
				)
				self.save_target_value((balance - sell_amount) * ohlcv[4])

		elif move <= -1*self.minimal_move:
			buy_amount = (target_balance - balance) * self.buy_modifier
			self.bot.log(
				"Buying {:f}. Reason: balance={:f}, target_balance={:f}, move={:f}, self.minimal_move={:f}".format(
					buy_amount, balance, target_balance, move, self.minimal_move
				),
				priority=1,
				extra_values=False
			)

			if self.buy(self.pair, buy_amount, ohlcv[4]):
				pprint(balance)
				pprint(buy_amount)
				pprint(ohlcv)
				self.bot.log(
					"Buying done. Setting target_value = %f" % ((balance + buy_amount) * ohlcv[4]),
					priority=1,
					extra_values=False
				)
				self.save_target_value((balance + buy_amount) * ohlcv[4])

	def command(self, chatbot, command: str, args=[]):
		command = command.lower()

		# TargetValue
		if command in ['target', 'targetvalue', 'target-value', 'target_value']:
			# Save new value
			if len(args) >= 1:
				if re.match(r'^[0-9.]+$', args[0]):
					self.save_target_value(args[0])

				else:
					chatbot.send_message(
						'Error: Value "`{:s}`" is not valid number.'.format(args[0])
					)

			# Send current value
			chatbot.send_message(
				'*Target value:* {:5.5f}'.format(self.get_target_value())
			)

		# Unsupported
		else:
			chatbot.send_message('Unsupported command "`{:s}`".'.format(command))


	################################################################################

	def buy(self, pair, amount, price):
		try:
			self.bot.log(
				"/keep_value/buy: Buying %f of %s for price %f" % (amount, pair, price),
				priority=1,
				extra_values=False
			)
			self.bot.buy(pair, amount, price)
			self.bot.log(
				"/keep_value/buy: Buy order sent.",
				priority=1,
				extra_values=False
			)

			self.error_sent = False
			self.bot.log(
				"/keep_value/buy: returning True.",
				priority=1,
				extra_values=False
			)
			return True

		except ccxt.InvalidOrder as e:
			self.bot.log(
				'Buy of {:5.5f} {:s} failed.'.format(amount, self.currency1),
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
				"/keep_value/sell: Selling %f of %s for price %f" % (amount, pair, price),
				priority=1,
				extra_values=False
			)
			self.bot.sell(pair, amount, price)
			self.bot.log(
				"/keep_value/sell: Sell order sent.",
				priority=1,
				extra_values=False
			)

			self.error_sent = False
			self.bot.log(
				"/keep_value/sell: returning True.",
				priority=1,
				extra_values=False
			)
			return True

		except ccxt.InvalidOrder as e:
			self.bot.log(
				'Sell of {:5.5f} {:s} failed...'.format(amount, self.currency1),
				priority=(1 if self.error_sent else 2)
			)
			self.bot.log(
				e,
				priority=(1 if self.error_sent else 2),
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
		self.bot.storage.save('target_value', float(target_value))
