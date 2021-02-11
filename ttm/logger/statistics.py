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

		self.bot = None

		# Prepare directory
		Path(output_folder).mkdir(parents=True, exist_ok=True)

	def log(self, message: str, bot, priority = 2, extra_values = {}):
		# Prepare
		if not self.bot:
			self.bot = bot

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

		if self.export_results:
			self.save_export_results()

	def get_metrics(self):
		return {
			'price': 'Price',
			'balance2': 'Cash balance',
			'relative_balance2': 'Risk cash balance',
			'value1': 'Crypto value',
			'total_value': 'Total value',
		}

	def print_summary(self):
		print('')

		#
		# OHLC
		#
		print('')
		headers = [
			'# OHLC',
			'Open',
			'High',
			'Low',
			'Close',
		]
		table = []
		for key, name in self.get_metrics().items():
			table.append(			[
				name,
				self.data[key][0],
				self.get_max(key),
				self.get_min(key),
				self.data[key][-1],
			])
		print(tabulate(table, headers=headers))

		#
		# Percentil
		#
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
		table = []
		for key, name in self.get_metrics().items():
			table.append(			[
				name,
				self.get_percentil(key, 10),
				self.get_percentil(key, 20),
				self.get_percentil(key, 30),
				self.get_percentil(key, 50),
				self.get_percentil(key, 70),
				self.get_percentil(key, 80),
				self.get_percentil(key, 90),
			])
		print(tabulate(table, headers=headers))

		#
		# Change
		#
		print('')
		headers = [
			'# CHANGE',
			'Total / Month',
			'Total / Year',
			'% / Month',
			'% / Year',
		]

		months = (self.data['date'][-1] - self.data['date'][0]).days / 31
		years = (self.data['date'][-1] - self.data['date'][0]).days / 365

		table = []
		for key, name in self.get_metrics().items():
			table.append(			[
				name,
				(self.data[key][-1] - self.data[key][0]) / months,
				(self.data[key][-1] - self.data[key][0]) / years,
				(self.data[key][-1] - self.data[key][0]) / months / (self.data[key][-1] - self.get_min(key)) * 100,
				(self.data[key][-1] - self.data[key][0]) / years / (self.data[key][-1] - self.get_min(key)) * 100,
			])
		print(tabulate(table, headers=headers))

	def save_export_results(self):
		#
		# Prepare csv file?
		#

		# Prepare directory
		directory = os.path.dirname(self.export_results['file'])
		Path(directory).mkdir(parents=True, exist_ok=True)

		# Prepare csv file
		if not os.path.exists(self.export_results['file']):
			with open(self.export_results['file'], 'w', newline='', encoding='utf8') as file:
				writer = csv.writer(file)

				# Prepare headers
				headers = ['Name', 'Open', 'High', 'Low', 'Close', '10p', '20p', '30p', '40p', '50p', '60p', '70p', '80p', '90p', 'Change / Month', 'Change / Year', '% / Month', '% / Year', 'Strategy', 'Exchange', 'From', 'To', 'Note']

				writer.writerow(headers)

		# Write data
		with open(self.export_results['file'], 'a', newline='', encoding='utf8') as file:
			writer = csv.writer(file)

			months = (self.data['date'][-1] - self.data['date'][0]).days / 31
			years = (self.data['date'][-1] - self.data['date'][0]).days / 365

			# Write to file
			for key, name in self.get_metrics().items():
				writer.writerow([
					name,
					self.data[key][0],
					self.get_max(key),
					self.get_min(key),
					self.data[key][-1],
					self.get_percentil(key, 10),
					self.get_percentil(key, 20),
					self.get_percentil(key, 30),
					self.get_percentil(key, 50),
					self.get_percentil(key, 70),
					self.get_percentil(key, 80),
					self.get_percentil(key, 90),
					(self.data[key][-1] - self.data[key][0]) / months,
					(self.data[key][-1] - self.data[key][0]) / years,
					(self.data[key][-1] - self.data[key][0]) / months / (self.data[key][-1] - self.get_min(key)) * 100,
					(self.data[key][-1] - self.data[key][0]) / years / (self.data[key][-1] - self.get_min(key)) * 100,
					type(self.bot.strategy).__name__,
					type(self.bot.exchange).__name__,
					self.get_results_date_from(),
					self.get_results_date_to(),
					self.export_results['note'],
				])

		self.clean_file(self.export_results['file'])

	def get_results_date_from(self):
		try:
			return self.bot.backtest_from
		except:
			pass

	def get_results_date_to(self):
		try:
			return self.bot.backtest_to
		except:
			pass

	def clean_file(self, file_path):
		#
		# Remove duplicated lines
		#
		unique_lines = []
		for line in open(file_path, "r"):
			if line not in unique_lines:  # check if line is not duplicate
				unique_lines.append(line)

		with open(file_path, "w") as output_file:
			output_file.write("".join(unique_lines))

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
