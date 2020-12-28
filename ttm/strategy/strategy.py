from datetime import datetime

"""
(This file is part of TTM package)

TTM - ToTheMoon crypto trading bot

@author  Michal Mikolas (nanuqcz@gmail.com)
"""
class Strategy(object):

	def __init__(self):
		# Config
		self.tick_period = 60           # seconds
		self.backtest_history_need = {  # seconds
			'BTC/USD-1m': 60*60*24      # just example: for 1m chart the strategy needs 24 hours history
		}

	def set_bot(self, bot):
		self.bot = bot

	def start(self):
		pass

	def tick(self):
		pass

	def finish(self):
		pass
