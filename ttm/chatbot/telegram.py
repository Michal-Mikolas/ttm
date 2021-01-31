import telepot
from telepot.loop import MessageLoop
from ttm.chatbot import Chatbot
import re
import shlex

"""
(This file is part of TTM package)

TTM - ToTheMoon crypto trading bot

@author  Michal Mikolas (nanuqcz@gmail.com)
"""
class Telegram(Chatbot):

	def __init__(self, token: str, password: str, root_folder = ''):
		super().__init__()

		self.telegram = telepot.Bot(token)
		self.password = password
		self.root_folder = root_folder

		self.chat_id = None

	def start(self):
		MessageLoop(self.telegram, self.on_message).run_as_thread()

	def send_message(self, message):
		self.telegram.sendMessage(self.chat_id, message, parse_mode='markdown')

	def on_message(self, msg):
		# Check
		if 'text' not in msg:
			return

		# Prepare
		content_type, chat_type, self.chat_id = telepot.glance(msg)
		args = self.fetch_args(msg['text'])

		# Call command
		if args[0] == 'status':
			self.command_status(args[1:])

		elif args[0] == 'how':
			self.command_status()

		elif args[0] == 'file':
			self.command_file(args[1:])

		elif args[0] == 'strategy':
			self.command_strategy(args[1:])

		else:
			self.command_start()

	def fetch_args(self, text):
		text = re.sub(r'^/', '', text)
		args = shlex.split(text)
		args[0] = args[0].lower()

		return args

	def command_status(self, args = []):
		#
		# Set new value?
		#
		if len(args) >= 1:
			self.bot.log(
				'Setting status="{:s}" ...'.format(args[0]),
				priority=2
			)
			self.bot.status = args[0]

		#
		# Prepare status data
		#
		output = '<pre>'

		pair = self.bot.get_last_pair()

		currency1, currency2 = None, None
		if pair:
			currency1, currency2 = self.bot.split_pair(pair)

		# Status
		output += 'Status:      {:s} \n'.format(self.bot.status)

		# Price
		price = None
		ohlcvs = self.bot.get_ohlcvs()
		if ohlcvs and currency2:
			price = ohlcvs[-1][3]
			output += 'Price:       {:5.5f} \n'.format(price)

		# Balances
		balance1, balance2 = None, None
		if pair and currency1 and currency2:
			balance1 = self.bot.get_balance(currency1)
			balance2 = self.bot.get_balance(currency2)

			output += 'Balance 1:   {:5.5f} \n'.format(balance1)
			output += 'Balance 2:   {:5.5f} \n'.format(balance2)

		# Values
		if price and balance1:
			output += 'Value 1:     {:5.5f} \n'.format(balance1 * price)
			output += 'Total value: {:5.5f} \n'.format(balance1 * price + balance2)

		output += '</pre>'

		#
		# Send data
		#
		self.telegram.sendMessage(self.chat_id, output, parse_mode='html')

	def command_file(self, args):
		# Prepare
		if len(args) == 0:
			self.send_message('Error: No file was specified.')
			return

		file_path = self.root_folder + '/' + args[0]

		number_of_lines = int(args[1]) if len(args) >= 2 else 3

		# Get file content
		last_lines = self.last_lines(file_path, number_of_lines)

		# Send file content
		self.send_message(
			'``` ... \n' + last_lines + ' ```'
		)

	def last_lines(self, fname, N):
		lines = ''

		try:
			with open(fname) as file:
				for line in (file.readlines() [-N:]):
					lines += line + '\n'

		finally:
			return lines

	def command_strategy(self, args):
		self.bot.strategy.command(self, args[0], args[1:])

	def command_start(self):
		self.telegram.sendMessage(
			self.chat_id,
			'Hello from TTM Trading Bot! \n'
			+ '\n'
			+ 'You can use following commands: \n'
			+ '/login password \n'
			+ '/status [active/paused/-] \n'
			+ '/file filename \n'
			+ '/strategy command [arg1, [arg2, [...]]] \n'
		)
