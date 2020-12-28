from ttm.statistics import Statistics

"""
(This file is part of TTM package)

TTM - ToTheMoon crypto trading bot

@author  Michal Mikolas (nanuqcz@gmail.com)
"""
class Fake(Statistics):

	def add(self, key, value):
		pass

	def get_percentil(self, key, percentil: float):
		return 0.0

	def get_median(self, key):
		return 0.0

	def get_min(self, key):
		return 0.0

	def get_max(self, key):
		return 0.0
