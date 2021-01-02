from ttm.logger import Logger
from ttm.bot import Bot
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

	def log(self, message: str, bot: Bot, *args):
		values = self.get_values(message, bot, *args)
		values = self.format_values(values)

		with open(self.file, 'a', newline='', encoding='utf8') as file:
			writer = csv.writer(file)
			writer.writerow(values)
