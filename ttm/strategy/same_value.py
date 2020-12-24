import math
from ttm.strategy import Strategy

class SameValue(Strategy):

	def __init__(self):
		super().__init__()

		# Config
		self.tick_period = 60  # seconds
		self.pair = 'BTC/USD'
		self.minimal_move = 5  # percent

		(self.currency1, self.currency1) = self.pair.split('/')

	def tick(self):
		ohlcvs = self.bot.get_ohlcvs(self.pair, '5m')
		ohlcv = ohlcvs[-1]

		last_price = self.get_last_price()
		move = (ohlcv[4] - last_price) / last_price * 100  # percent
		# print('(%d - %d) / %d * 100 = %d' % (ohlcv[4], last_price, last_price, move)) ###

		if move >= self.minimal_move:
			balance = self.bot.get_balance(self.currency1)

			buy_amount = balance * move / 100
			self.bot.sell(self.pair, buy_amount)

			self.bot.storage.save('last_price', ohlcv[4])
			# self.bot.log(self, 'Bought %f %s.' % (buy_amount, self.currency1))

		elif move <= -1*self.minimal_move:
			balance = self.bot.get_balance(self.currency1)

			sell_amount = last_price * move / 100
			self.bot.buy(self.pair, sell_amount)

			self.bot.storage.save('last_price', ohlcv[4])
			# self.bot.log(self, 'Sold %f %s.' % (sell_amount, self.currency1))

	def get_last_price(self):
		last_price = self.bot.storage.get('last_price')

		if not last_price:
			last_price = self.bot.get_ohlcvs(self.pair, '5m')[-1][4]
			self.bot.storage.save('last_price', last_price)

		return last_price
