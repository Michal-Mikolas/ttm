import ccxt

class BinanceFix(ccxt.binance):
	def get_step_size(self, pair):
		filters = pairs['BTC/USDT']['market']['info']['filters']
		filter = [v for v in filters if v['filterType'] == 'LOT_SIZE'][0]
		step_size = filter['stepSize']
		return step_size

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
