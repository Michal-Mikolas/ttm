from datetime import datetime

class Logger():

	def log(self, *args):
		raise NotImplementedError

	def format_values(self, values):
		return [self.format_value(x) for x in values]

	def format_value(self, value):
		if type(value) is datetime:
			return value.strftime('%Y-%m-%d %H:%M:%S')

		return value
