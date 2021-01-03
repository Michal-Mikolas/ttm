import yagmail
from ttm.logger import Logger

"""
(This file is part of TTM package)

TTM - ToTheMoon crypto trading bot

@author  Michal Mikolas (nanuqcz@gmail.com)
"""
class Gmail(Logger):

	def __init__(self, to: str, login: str, password: str = None, subject='TTM - Notification'):
		super().__init__()

		self.to = to
		self.yag = yagmail.SMTP(login, password)
		self.subject = subject

	def log(self, message: str, bot, *args):
		values = self.get_values(message, bot, *args)
		values = self.format_values(values)

		values = [str(value) for value in values]
		body = ' | '.join(values)

		self.yag.send(self.to, self.subject, body)
