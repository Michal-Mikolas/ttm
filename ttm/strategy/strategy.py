from datetime import datetime

class Strategy(object):

	def __init__(self, bot):
		self.bot = bot

		# Config
		self.tick_period = 60           # seconds
		self.backtest_history_need = {  # seconds
			'BTC/USD-1m': 60*60*24
		}

	def tick(self):
		pass
