from ttm.logger import Logger
import csv

class CSVFile(Logger):

	def __init__(self, file: str):
		super().__init__()

		self.file = file

	def log(self, *args):
		with open(self.file, 'a', newline='', encoding='utf8') as file:
			values = self.format_values(args)

			writer = csv.writer(file)
			writer.writerow(values)
