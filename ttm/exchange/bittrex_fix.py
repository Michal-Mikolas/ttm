import ccxt

class BittrexFix(ccxt.bittrex):
	def create_order(self, symbol, type, side, amount, price=None, params={}):
		if (('createMarketBuyOrderRequiresPrice' in self.options)
			and (self.options['createMarketBuyOrderRequiresPrice'] is False)
			and (type == 'market')
			and (side == 'buy')
		):
			type = 'CEILING_MARKET'
			return super().create_order(symbol, type, side, amount, price, params)

		else:
			return super().create_order(symbol, type, side, amount, price, params)
