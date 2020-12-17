import math

class SameValue(Strategy):

	def __init__(self, bot):
		super.__init__(self, bot)

		# Config
		self.minimal_move = 5  # percent

	def tick(self):
		candles = self.bot.get_candles(self.pair, '5m')
		candle = candles[-1]

		balance = self.bot.get_balance('BTC')
		last_price = self.bot.storage('last_price')
		move = (candle['close'] - last_price) / last_price * 100  # percent

		if (move >= self.minimal_move):
			self.bot.sell(
				self.pair,
				balance * move / 100
			)

		else:
			self.bot.buy(
				self.pair,
				last_price * move / 100
			)
