from ttm.logger import Logger
import csv

"""
(This file is part of TTM package)

TTM - ToTheMoon crypto trading bot

@author  Michal Mikolas (nanuqcz@gmail.com)
"""
class CSVFile(Logger):

	def __init__(self, file: str):
		super().__init__()

		self.file = file

	def log(self, *args):
		with open(self.file, 'a', newline='', encoding='utf8') as file:
			values = self.format_values(args)

			writer = csv.writer(file)
			writer.writerow(values)
