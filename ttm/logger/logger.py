from datetime import datetime

"""
(This file is part of TTM package)

TTM - ToTheMoon crypto trading bot

@author  Michal Mikolas (nanuqcz@gmail.com)
"""
class Logger():

	def set_pair(self, pair: str):
		self.pair = pair

	def log(self, message: str, bot, priority = 2, extra_values = {}):
		raise NotImplementedError

	def get_values(self, message: str, bot, extra_values = {}):
		# Basic values
		values = {
			'date': bot.now(),
			'message': message,
		}

		# Pair-related values
		if self.pair and extra_values is not False:
			(currency1, currency2) = bot.split_pair(self.pair)

			ohlcvs = bot.get_ohlcvs(self.pair)
			if ohlcvs:
				price = ohlcvs[-1][4]
				balance1 = bot.get_balance(currency1)
				balance2 = bot.get_balance(currency2)

				values.update({
					'price':             price,
					'balance1':          balance1,
					'balance2':          balance2,
					'value1':            balance1 * price,
					'total_value':       balance1 * price + balance2,
				})

		# Extra values
		if extra_values:
			values.update(extra_values)

		# Return
		return values

	def format_values(self, values):
		return {key: self.format_value(values[key]) for key in values}

	def format_value(self, value):
		if type(value) is datetime:
			return value.strftime('%Y-%m-%d %H:%M:%S')

		return value
