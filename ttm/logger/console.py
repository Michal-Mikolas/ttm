from ttm.logger import Logger
from datetime import datetime

"""
(This file is part of TTM package)

TTM - ToTheMoon crypto trading bot

@author  Michal Mikolas (nanuqcz@gmail.com)
"""
class Console(Logger):

	def __init__(self):
		pass

	def log(self, message: str, bot, *args):
		values = self.get_values(message, bot, *args)

		output = ''
		for value in values:
			output += self.format_value(value)

		print(output)

	def format_value(self, value):
		if type(value) is str:
			value = "{:24s}".format(value)

		if type(value) is datetime:
			value = "{:20s}".format(value.strftime('%Y-%m-%d %H:%M:%S'))

		if type(value) is int:
			value = "{:6d}".format(value)
			value = value.rjust(6) + '  '

		if type(value) is float:
			value = "{:5.6f}".format(value)
			value = value.rjust(13) + '  '

		return value

