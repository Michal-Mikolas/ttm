from ttm.logger import Logger

"""
(This file is part of TTM package)

TTM - ToTheMoon crypto trading bot

@author  Michal Mikolas (nanuqcz@gmail.com)
"""
class Multi(Logger):

	def __init__(self, *args):
		super().__init__()

		self.loggers = args

	def log(self, *args):
		[logger.log(*args) for logger in self.loggers]

	def set_pair(self, pair):
		[logger.set_pair(pair) for logger in self.loggers]
