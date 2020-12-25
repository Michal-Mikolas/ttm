from ttm.logger import Logger
from datetime import datetime

class Console(Logger):

	def __init__(self):
		pass

	def log(self, *args):
		output = ''
		for arg in args:
			output += self.format_value(arg, fixed_size=True)

		print(output)

	def format_values(self, values, fixed_size=False):
		return [self.format_value(x, fixed_size) for x in values]

	def format_value(self, value, fixed_size=False):
		if fixed_size:
			if type(value) is str:
				value = "{:36s}".format(value)

			if type(value) is datetime:
				value = "{:22s}".format(value.strftime('%Y-%m-%d %H:%M:%S'))

			if type(value) is int:
				value = "{:8d}".format(value)
				value = value.rjust(8) + '  '

			if type(value) is float:
				value = "{:6.8f}".format(value)
				value = value.rjust(15) + '  '

		else:
			value = super().format_value(value)

		return value

