from ttm.logger import Logger
from pathlib import Path
from datetime import datetime

"""
(This file is part of TTM package)

TTM - ToTheMoon crypto trading bot

@author  Michal Mikolas (nanuqcz@gmail.com)
"""
class Statistics(Logger):

	def __init__(self, storage, output_folder = None):
		self.storage = storage
		self.output_folder = output_folder

		# Prepare directory
		Path(output_folder).mkdir(parents=True, exist_ok=True)

	def log(self, message: str, bot, extra_values = {}):
		values = self.get_values(message, bot, extra_values)

		# TODO
		for key in values:
			pass


	 #####
	#     # #####   ##   ##### #  ####  ##### #  ####   ####
	#         #    #  #    #   # #        #   # #    # #
	 #####    #   #    #   #   #  ####    #   # #       ####
	      #   #   ######   #   #      #   #   # #           #
	#     #   #   #    #   #   # #    #   #   # #    # #    #
	 #####    #   #    #   #   #  ####    #   #  ####   ####

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

	 #####
	#     # #####  ####  #####    ##    ####  ######
	#         #   #    # #    #  #  #  #    # #
	 #####    #   #    # #    # #    # #      #####
	      #   #   #    # #####  ###### #  ### #
	#     #   #   #    # #   #  #    # #    # #
	 #####    #    ####  #    # #    #  ####  ######

	def get(self, key):
		return self.storage.get('statistics_' + key)

	def save(self, key, value):
		return self.storage.save('statistics_' + key, value)
