from ttm.logger import Logger

class Multi(Logger):

	def __init__(self, *args):
		super().__init__()

		self.loggers = args

	def log(self, *args):
		[logger.log(*args) for logger in self.loggers]
