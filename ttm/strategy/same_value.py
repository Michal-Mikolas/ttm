from datetime import datetime
from ttm.strategy import Strategy

class SameValue(Strategy):

	def __init__(self, pair='BTC/USD', minimal_move=5, tick_period=60, timeframe='1m'):
		super().__init__()

		# Config
		self.pair = pair
		self.minimal_move = minimal_move  # percent
		self.tick_period = tick_period    # seconds
		self.timeframe = timeframe

		(self.currency1, self.currency2) = self.pair.split('/')

	def tick(self):
		ohlcvs = self.bot.get_ohlcvs(self.pair, self.timeframe)
		ohlcv = ohlcvs[-1]

		last_price = self.get_last_price()
		move = (ohlcv[4] - last_price) / last_price * 100  # percent
		# print('(%d - %d) / %d * 100 = %d' % (ohlcv[4], last_price, last_price, move)) ###

		if move >= self.minimal_move:
			balance = self.bot.get_balance(self.currency1)

			sell_amount = balance * move / 100
			self.bot.sell(self.pair, sell_amount)

			self.bot.storage.save('last_price', ohlcv[4])
			self.bot.log(datetime.utcfromtimestamp(ohlcv[0]/1000), ohlcv[4], 'Sold %f %s.' % (sell_amount, self.currency1), self.bot.get_balance(self.currency1), self.bot.get_balance(self.currency2))

		elif move <= -1*self.minimal_move:
			balance = self.bot.get_balance(self.currency1)

			buy_amount = -1 * balance * move / 100  # -1: move is negative number here
			self.bot.buy(self.pair, buy_amount)

			self.bot.storage.save('last_price', ohlcv[4])
			self.bot.log(datetime.utcfromtimestamp(ohlcv[0]/1000), ohlcv[4], 'Bought %f %s.' % (buy_amount, self.currency1), self.bot.get_balance(self.currency1), self.bot.get_balance(self.currency2))

	def get_last_price(self):
		last_price = self.bot.storage.get('last_price')

		if not last_price:
			last_price = self.bot.get_ohlcvs(self.pair, self.timeframe)[-1][4]
			self.bot.storage.save('last_price', last_price)

		return last_price
