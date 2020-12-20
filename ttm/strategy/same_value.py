import math
from ttm.bot import Bot

class SameValue(Strategy):

	def __init__(self, bot: Bot):
		super.__init__(self, bot)

		# Config
		self.tick_period = '60'
		self.pair = 'BTC/USD'
		self.minimal_move = 5  # percent

	def tick(self):
		ohlcvs = self.bot.get_ohlcvs(self.pair, '5m')
		ohlcv = ohlcvs[-1]

		balance = self.bot.get_balance('BTC')
		last_price = self.bot.storage('last_price')
		move = (ohlcv['4'] - last_price) / last_price * 100  # percent

		if move >= self.minimal_move:
			self.bot.sell(
				self.pair,
				balance * move / 100
			)

		else if move <= -self.minimal_move:
			self.bot.buy(
				self.pair,
				last_price * move / 100
			)
