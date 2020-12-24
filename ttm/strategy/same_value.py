import math
from ttm.strategy import Strategy

class SameValue(Strategy):

	def __init__(self):
		super().__init__()

		# Config
		self.tick_period = 60  # seconds
		self.pair = 'BTC/USD'
		self.minimal_move = 5  # percent

	def tick(self):
		ohlcvs = self.bot.get_ohlcvs(self.pair, '5m')
		ohlcv = ohlcvs[-1]

		last_price = self.get_last_price()
		move = (ohlcv[4] - last_price) / last_price * 100  # percent
		print('(%d - %d) / %d * 100 = %d' % (ohlcv[4], last_price, last_price, move)) ###

		if move >= self.minimal_move:
			balance = self.bot.get_balance('BTC')
			self.bot.sell(
				self.pair,
				balance * move / 100
			)
			self.bot.storage.save('last_price', ohlcv[4])

		elif move <= -1*self.minimal_move:
			balance = self.bot.get_balance('BTC')
			self.bot.buy(
				self.pair,
				last_price * move / 100
			)
			self.bot.storage.save('last_price', ohlcv[4])

	def get_last_price(self):
		last_price = self.bot.storage.get('last_price')

		if not last_price:
			last_price = self.bot.get_ohlcvs(self.pair, '5m')[-1][4]
			self.bot.storage.save('last_price', last_price)

		return last_price
