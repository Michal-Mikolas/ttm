from ttm.logger import Logger
from pathlib import Path
from tabulate import tabulate
import os
from pathlib import Path
import csv

"""
(This file is part of TTM package)

TTM - ToTheMoon crypto trading bot

@author  Michal Mikolas (nanuqcz@gmail.com)
"""
class Statistics(Logger):

	def __init__(self, storage, output_folder = None, min_priority = 0, export_results = None):
		self.data = {}  # TODO change to storage
		self.storage = storage
		self.output_folder = output_folder
		self.min_priority = min_priority
		self.export_results = export_results

		# Prepare directory
		Path(output_folder).mkdir(parents=True, exist_ok=True)

	def log(self, message: str, bot, priority = 2, extra_values = {}):
		# Prepare
		if priority < self.min_priority:
			return

		values = self.get_values(message, bot, extra_values)
		if 'price' not in values:
			return

		# Save current values
		self.add('date', values['date'])
		self.add('price', values['price'])
		self.add('balance1', values['balance1'])
		self.add('balance2', values['balance2'])
		self.add('relative_balance2', values['relative_balance2'])
		self.add('value1', values['value1'])
		self.add('total_value', values['total_value'])

	 #####
	#     # #    # #    # #    #   ##   #####  #   #
	#       #    # ##  ## ##  ##  #  #  #    #  # #
	 #####  #    # # ## # # ## # #    # #    #   #
	      # #    # #    # #    # ###### #####    #
	#     # #    # #    # #    # #    # #   #    #
	 #####   ####  #    # #    # #    # #    #   #

	def __del__(self):
		self.print_summary()

		# if self.export_results:
		# 	self.save_export_results()

	def print_summary(self):
		print('')

		print('')
		headers = [
			'# OHLC',
			'Open',
			'High',
			'Low',
			'Close',
		]
		table = [
			[
				'Price',
				self.data['price'][0],
				self.get_max('price'),
				self.get_min('price'),
				self.data['price'][-1],
			],
			[
				'Cash balance',
				self.data['balance2'][0],
				self.get_max('balance2'),
				self.get_min('balance2'),
				self.data['balance2'][-1],
			],
			[
				'Risk cash balance',
				self.data['relative_balance2'][0],
				self.get_max('relative_balance2'),
				self.get_min('relative_balance2'),
				self.data['relative_balance2'][-1],
			],
			[
				'Crypto value',
				self.data['value1'][0],
				self.get_max('value1'),
				self.get_min('value1'),
				self.data['value1'][-1],
			],
			[
				'Total value',
				self.data['total_value'][0],
				self.get_max('total_value'),
				self.get_min('total_value'),
				self.data['total_value'][-1],
			],
		]
		print(tabulate(table, headers=headers))

		print('')
		headers = [
			'# PERCENTIL',
			'10p',
			'20p',
			'30p',
			'50p',
			'70p',
			'80p',
			'90p',
		]
		table = [
			[
				'Price',
				self.get_percentil('price', 10),
				self.get_percentil('price', 20),
				self.get_percentil('price', 30),
				self.get_percentil('price', 50),
				self.get_percentil('price', 70),
				self.get_percentil('price', 80),
				self.get_percentil('price', 90),
			],
			[
				'Cash balance',
				self.get_percentil('balance2', 10),
				self.get_percentil('balance2', 20),
				self.get_percentil('balance2', 30),
				self.get_percentil('balance2', 50),
				self.get_percentil('balance2', 70),
				self.get_percentil('balance2', 80),
				self.get_percentil('balance2', 90),
			],
			[
				'Risk cash balance',
				self.get_percentil('relative_balance2', 10),
				self.get_percentil('relative_balance2', 20),
				self.get_percentil('relative_balance2', 30),
				self.get_percentil('relative_balance2', 50),
				self.get_percentil('relative_balance2', 70),
				self.get_percentil('relative_balance2', 80),
				self.get_percentil('relative_balance2', 90),
			],
			[
				'Crypto value',
				self.get_percentil('value1', 10),
				self.get_percentil('value1', 20),
				self.get_percentil('value1', 30),
				self.get_percentil('value1', 50),
				self.get_percentil('value1', 70),
				self.get_percentil('value1', 80),
				self.get_percentil('value1', 90),
			],
			[
				'Total value',
				self.get_percentil('total_value', 10),
				self.get_percentil('total_value', 20),
				self.get_percentil('total_value', 30),
				self.get_percentil('total_value', 50),
				self.get_percentil('total_value', 70),
				self.get_percentil('total_value', 80),
				self.get_percentil('total_value', 90),
			],
		]
		print(tabulate(table, headers=headers))

		print('')
		headers = [
			'# PROFIT',
			'Amount / Month',
			'Amount / Year',
			'% / Month',
			'% / Year',
		]

		months = (self.data['date'][-1] - self.data['date'][0]).days / 31
		years = (self.data['date'][-1] - self.data['date'][0]).days / 365
		total_cache_invested = self.data['value1'][0] - self.get_min('balance2')  # initial crypto buy - not user cash

		table = [
			[
				'Total value',
				(self.data['total_value'][-1] - self.data['total_value'][0]) / months,
				(self.data['total_value'][-1] - self.data['total_value'][0]) / years,
				# total_value_profit / total_cache_invested / days_count * 31 * 100
				(self.data['total_value'][-1] - self.data['total_value'][0]) / total_cache_invested / months * 100,
				# total_value_profit / total_cache_invested / days_count * 365 * 100
				(self.data['total_value'][-1] - self.data['total_value'][0]) / total_cache_invested / years * 100,
			],
			[
				'Cash',
				(self.data['balance2'][-1] - self.data['balance2'][0]) / months,
				(self.data['balance2'][-1] - self.data['balance2'][0]) / years,
				# profit / total_cache_invested / days_count * 31 * 100
				(self.data['balance2'][-1] - self.data['balance2'][0]) / total_cache_invested / months * 100,
				# profit / total_cache_invested / days_count * 365 * 100
				(self.data['balance2'][-1] - self.data['balance2'][0]) / total_cache_invested / years * 100,
			],
			[
				'(Price)',
				(self.data['price'][-1] - self.data['price'][0]) / months,
				(self.data['price'][-1] - self.data['price'][0]) / years,
				(self.data['price'][-1] - self.data['price'][0]) / self.data['price'][0] / months * 100,
				(self.data['price'][-1] - self.data['price'][0]) / self.data['price'][0] / years * 100,
			],
		]
		print(tabulate(table, headers=headers))

	def save_export_results(self):
		#
		# Prepare csv file?
		#

		# Prepare directory
		directory = os.path.dirname(self.export_results['file'])
		Path(directory).mkdir(parents=True, exist_ok=True)

		# Prepare csv file
		with open(self.export_results['file'], 'a', newline='', encoding='utf8') as file:
			writer = csv.writer(file)

			# Prepare headers
			headers = ['', 'Open', 'High', 'Low', 'Close', '10p', '20p', '30p', '40p', '50p', '60p', '70p', '80p', '90p', 'Profit / Month', 'Profit / Year', 'Profit % / Month', 'Profit % / Year']

			if 'extra_values' in self.export_results:
				headers.update(self.export_results['extra_values'].keys())

			# Write to file
			writer.writerow(headers)


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
