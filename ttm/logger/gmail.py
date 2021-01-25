import yagmail
from ttm.logger import Logger

"""
(This file is part of TTM package)

TTM - ToTheMoon crypto trading bot

@author  Michal Mikolas (nanuqcz@gmail.com)
"""
class Gmail(Logger):

	def __init__(self, to: str, login: str, password: str = None, subject='TTM Bot- Notification', min_priority = 2):
		super().__init__()

		self.to = to
		self.yag = yagmail.SMTP(login, password)
		self.subject = subject
		self.min_priority = min_priority

	def log(self, message: str, bot, priority = 2, extra_values = {}):
		if priority < self.min_priority:
			return

		values = self.get_values(message, bot, extra_values)
		values = self.format_values(values)

		values = [str(value) for value in values.values()]
		body = ' | '.join(values)

		self.yag.send(self.to, self.subject, body)
