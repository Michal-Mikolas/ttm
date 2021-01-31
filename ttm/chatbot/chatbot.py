"""
(This file is part of TTM package)

TTM - ToTheMoon crypto trading bot

@author  Michal Mikolas (nanuqcz@gmail.com)
"""
class Chatbot(object):

	def __init__(self):
		self.bot = None

	# Sets the trading bot
	def set_bot(self, bot):
		self.bot = bot

	def start(self):
		pass

	def send_message(self, message):
		pass
