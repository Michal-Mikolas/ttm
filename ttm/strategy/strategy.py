class Strategy(object):

	def __init__(self, bot):
		self.bot = bot

		# Config
		self.tick_period = '60'
		self.pair = 'BTC/EUR'

	def tick(self):
		pass
