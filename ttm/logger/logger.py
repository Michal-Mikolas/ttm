from datetime import datetime
from ttm.bot import Bot

"""
(This file is part of TTM package)

TTM - ToTheMoon crypto trading bot

@author  Michal Mikolas (nanuqcz@gmail.com)
"""
class Logger():

	def set_pair(self, pair: str):
		self.pair = pair

	def log(self, message: str, bot: Bot, *args):
		raise NotImplementedError

	def get_values(self, message: str, bot: Bot, *args):
		# Basic values
		values = [
			bot.now(),
			message,
		]

		# Pair-related values
		if self.pair:
			(currency1, currency2) = bot.split_pair(self.pair)

			price = bot.get_ohlcvs()[-1][4]
			balance1 = bot.get_balance(currency1)
			balance2 = bot.get_balance(currency2)

			# Relative balance
			last_balance2 = bot.storage.get('last_balance2') or 0.0
			balance2_change = balance2 - last_balance2
			last_relative_balance2 = bot.storage.get('last_relative_balance2') or 0.0
			relative_balance2 = last_relative_balance2 + balance2_change
			relative_balance2 = relative_balance2 if relative_balance2 < 0.0 else 0.0

			values = values + [
				price,
				balance1,
				balance2,
				relative_balance2,
				balance1 * price,            # value 1
				balance1 * price + balance2  # total value
			]

		# Extra values
		values = values + args

		# Return
		return values

	def format_values(self, values):
		return [self.format_value(x) for x in values]

	def format_value(self, value):
		if type(value) is datetime:
			return value.strftime('%Y-%m-%d %H:%M:%S')

		return value
