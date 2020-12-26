from datetime import datetime
from ttm.strategy import Strategy

class SameValue(Strategy):

	def __init__(self, pair: str, initial_target_value: float, minimal_move=5.0, tick_period=60, timeframe='1m', sell_modifier=1.00, buy_modifier=1.00):
		super().__init__()

		# Config
		self.pair = pair
		self.initial_target_value = initial_target_value
		self.minimal_move = minimal_move    # percent
		self.tick_period = tick_period      # seconds
		self.timeframe = timeframe
		self.sell_modifier = sell_modifier  # percent
		self.buy_modifier = buy_modifier    # percent

		(self.currency1, self.currency2) = self.pair.split('/')  # TODO fix for values like 'BTCUSD'?

	def start(self):
		ohlcv = self.bot.get_ohlcvs(self.pair, self.timeframe)[-1]
		self.log('Start', ohlcv, self.bot.get_balance(self.currency1), self.bot.get_balance(self.currency2))

	def tick(self):
		ohlcv = self.bot.get_ohlcvs(self.pair, self.timeframe)[-1]
		balance = self.bot.get_balance(self.currency1)

		target_balance = self.get_target_value() / ohlcv[4]
		move = (balance - target_balance) / target_balance * 100  # percent

		if move >= self.minimal_move:
			sell_amount = (balance - target_balance) * self.sell_modifier

			self.bot.sell(self.pair, sell_amount)
			self.save_target_value((balance - sell_amount) * ohlcv[4])

			self.log('Sold %f %s.' % (sell_amount, self.currency1), ohlcv, self.bot.get_balance(self.currency1), self.bot.get_balance(self.currency2))

		elif move <= -1*self.minimal_move:
			buy_amount = (target_balance - balance) * self.buy_modifier

			self.bot.buy(self.pair, buy_amount)
			self.save_target_value((balance + buy_amount) * ohlcv[4])

			self.log('Bought %f %s.' % (buy_amount, self.currency1), ohlcv, self.bot.get_balance(self.currency1), self.bot.get_balance(self.currency2))

	def finish(self):
		ohlcv = self.bot.get_ohlcvs(self.pair, self.timeframe)[-1]
		self.log('Finish', ohlcv, self.bot.get_balance(self.currency1), self.bot.get_balance(self.currency2))

	################################################################################

	def get_target_value(self):
		target_value = self.bot.storage.get('target_value')

		if not target_value:
			target_value = self.initial_target_value
			self.bot.storage.save('target_value', target_value)

		return target_value

	def save_target_value(self, target_value):
		self.bot.storage.save('target_value', target_value)

	def log(self, message: str, ohlcv, balance1: float, balance2: float):
		last_balance2 = self.bot.storage.get('last_balance2') or 0.0
		balance2_change = balance2 - last_balance2

		last_relative_balance2 = self.bot.storage.get('last_relative_balance2') or 0.0
		relative_balance2 = last_relative_balance2 + balance2_change
		relative_balance2 = relative_balance2 if relative_balance2 < 0.0 else 0.0

		self.bot.log(
			datetime.utcfromtimestamp(ohlcv[0]/1000),  # datetime
			ohlcv[4],                                  # price
			message,                                   # message
			balance1,                                  # balance 1
			balance2,                                  # balance 2
			relative_balance2,                         # relative balance 2
			balance1 * ohlcv[4],                       # value 1
			balance1 * ohlcv[4] + balance2             # total value
		)

		self.bot.storage.save('last_balance2', balance2)
		self.bot.storage.save('last_relative_balance2', relative_balance2)
