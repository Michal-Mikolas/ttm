from ttm.statistics import Statistics

"""
(This file is part of TTM package)

TTM - ToTheMoon crypto trading bot

@author  Michal Mikolas (nanuqcz@gmail.com)
"""
class Real(Statistics):

	def add(self, key, value):
		if key not in self.data:
			self.data[key] = []

		self.data[key].append(value)

	def get_percentil(self, key, percentil: float):
		if key not in self.data:
			return None

		data = sorted(self.data[key])

		size = len(data)
		index = round(size * percentil / 100)

		return data[index]

	def get_median(self, key):
		return self.get_percentil(key, 50)

	def get_min(self, key):
		if key not in self.data:
			return None

		return min(self.data[key])

	def get_max(self, key):
		if key not in self.data:
			return None

		return max(self.data[key])
