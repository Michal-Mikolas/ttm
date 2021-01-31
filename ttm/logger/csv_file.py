from ttm.logger import Logger
import os
from pathlib import Path
import csv

"""
(This file is part of TTM package)

TTM - ToTheMoon crypto trading bot

@author  Michal Mikolas (nanuqcz@gmail.com)
"""
class CSVFile(Logger):

	def __init__(self, file: str, min_priority = 1):
		super().__init__()
		self.columns = 0

		self.file = file
		self.min_priority = min_priority

		# Prepare directory
		directory = os.path.dirname(self.file)
		Path(directory).mkdir(parents=True, exist_ok=True)

	def log(self, message: str, bot, priority = 2, extra_values = {}):
		if priority < self.min_priority:
			return

		# Prepare
		values = self.get_values(message, bot, extra_values)
		values = self.format_values(values)

		with open(self.file, 'a', newline='', encoding='utf8') as file:
			writer = csv.writer(file)

			# Write header?
			if len(values) > self.columns:
				writer.writerow(values.keys())

			# Write data
			writer.writerow(values.values())

		# Finish
		self.columns = max(self.columns, len(values))
