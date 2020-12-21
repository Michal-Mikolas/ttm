from datetime import datetime

class Strategy(object):

	def __init__(self):
		# Config
		self.tick_period = 60           # seconds
		self.backtest_history_need = {  # seconds
			'BTC/USD-1m': 60*60*24      # just example: for 1m chart the strategy needs 24 hours history
		}

	def set_bot(self, bot):
		self.bot = bot

	def tick(self):
		pass
