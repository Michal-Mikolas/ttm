import ccxt

class BinanceFix(ccxt.binance):

	def __init__(self, options):
		super().__init__(options)

		self.cache = {
			'get_step_size': {},
		}

	def get_step_size(self, pair):
		if pair not in self.cache['get_step_size']:
			markets = self.fetch_markets()
			for market in markets:
				filter = [v for v in market['info']['filters'] if v['filterType'] == 'LOT_SIZE'][0]
				self.cache['get_step_size'][market['symbol']] = float(filter['stepSize'])

		return self.cache['get_step_size'][pair]

	def create_order(self, symbol, type, side, amount, price=None, params={}):
		step_size = self.get_step_size(symbol)

		mod = amount % step_size
		if mod != 0.0:
			# Round amount to step_size
			r = mod / step_size
			if r < 0.5:
				amount = amount - mod
			else:
				amount = amount - mod + step_size

		super().create_order(symbol, type, side, amount, price, params)
