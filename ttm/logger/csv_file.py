from ttm.logger import Console
import csv

class CSVFile(Console):

	def __init__(self, file: str, print_to_console = True):
		super().__init__()

		self.file = file
		self.print_to_console = print_to_console

	def log(self, *args):
		if self.print_to_console:
			super().log(*args)

		with open(self.file, 'a', newline='', encoding='utf8') as file:
			values = self.format_values(args, fixed_size=False)

			writer = csv.writer(file)
			writer.writerow(values)
