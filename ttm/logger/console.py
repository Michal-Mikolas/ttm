from ttm.logger import Logger
from datetime import datetime

"""
(This file is part of TTM package)

TTM - ToTheMoon crypto trading bot

@author  Michal Mikolas (nanuqcz@gmail.com)
"""
class Console(Logger):

	def __init__(self, min_priority = 0):
		self.columns = 0
		self.counter = 0

		self.min_priority = min_priority

	def log(self, message: str, bot, priority = 2, extra_values = {}):
		if priority < self.min_priority:
			return

		# Prepare
		values = self.get_values(message, bot, extra_values)

		# Print header?
		if (self.counter % 10 == 0) or (self.columns < len(values)):
			self.print_header(values)

		# Print values
		output = ''
		for (key, value) in values.items():
			output += self.format_value(value)

		print(output)

		# Finish
		self.columns = len(values)
		self.counter += 1

	def format_value(self, value):
		if type(value) is str:
			value = "{:30s}".format(value)

		elif type(value) is datetime:
			value = "{:21s}".format(value.strftime('%Y-%m-%d %H:%M:%S'))

		elif type(value) is int:
			value = "{:6d}".format(value)
			value = value.rjust(6) + '  '

		elif type(value) is float:
			value = "{:5.6f}".format(value)
			value = value.rjust(12) + '  '

		else:
			value = "{:24s}".format(value)

		return value

	def print_header(self, values):
		output = ''

		for key in values:
			value = values[key]
			header = key.capitalize()

			if type(value) is str:
				header = "{:30s}".format(header[0:30])

			elif type(value) is datetime:
				header = "{:21s}".format(header[0:21])

			elif type(value) is int:
				# header = "{:6s}".format(header[0:6])
				header = header[0:6]
				header = header.rjust(6) + '  '

			elif type(value) is float:
				# header = "{:12s}".format(header[0:12])
				header = header[0:12]
				header = header.rjust(12) + '  '

			else:
				header = "{:24s}".format(header[0:24])

			output += header

		print('=' * len(output))
		print(output)
		print('=' * len(output))
