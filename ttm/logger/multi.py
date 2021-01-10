from ttm.logger import Logger

"""
(This file is part of TTM package)

TTM - ToTheMoon crypto trading bot

@author  Michal Mikolas (nanuqcz@gmail.com)
"""
class Multi(Logger):

	def __init__(self, *loggers):
		super().__init__()

		self.loggers = loggers

	def set_pair(self, pair):
		[logger.set_pair(pair) for logger in self.loggers]

	def log(self, message: str, bot, extra_values={}):
		[logger.log(message, bot, extra_values) for logger in self.loggers]
