import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton
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
		self.sessions = {}
		self.msg_history = {}

	def start(self):
		MessageLoop(self.telegram, self.on_message).run_as_thread()

	def send_message(self, message):
		self.telegram.sendMessage(
			self.chat_id,
			message,
			parse_mode='markdown',
			reply_markup=self.get_history_keyboard()
		)

	def on_message(self, msg):
		#
		# Check & Prepare
		#

		# args
		if 'text' not in msg:
			return
		args = self.fetch_args(msg['text'])

		content_type, chat_type, self.chat_id = telepot.glance(msg)

		# Security
		if args[0] not in ['start', 'login', 'hello', 'hi']:
			is_logged_in = self.handle_security()
			if not is_logged_in:
				return

		# Command history
		self.history(msg['text'])

		#
		# Call command
		#
		if args[0] == 'login':
			self.command_login(args[1:])

		elif args[0] == 'logout':
			self.command_logout(args[1:])

		elif args[0] == 'status':
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

	def handle_security(self):
		# Check
		is_logged_in = False
		try:
			if self.sessions[self.chat_id]['password'] == self.password:
				is_logged_in = True
		except KeyError:
			pass

		# Alert
		if not is_logged_in:
			self.send_message('You are not logged in. Please use following command to login: \n\n/login password')

		# Return
		return is_logged_in

	#     #
	#     # #  ####  #####  ####  #####  #   #
	#     # # #        #   #    # #    #  # #
	####### #  ####    #   #    # #    #   #
	#     # #      #   #   #    # #####    #
	#     # # #    #   #   #    # #   #    #
	#     # #  ####    #    ####  #    #   #

	def history(self, msg:str = None):
		# Prepare
		if self.chat_id not in self.msg_history:
			self.msg_history[self.chat_id] = []

		# Save last msg
		if msg and not re.match(r'/?login', msg.lower()):
			# remove msg if already in history
			self.msg_history[self.chat_id] = [v for v in self.msg_history[self.chat_id] if v != msg]
			# append it to the end
			self.msg_history[self.chat_id].append(msg)
			# keep only last 4 msgs
			self.msg_history[self.chat_id] = self.msg_history[self.chat_id][-4:]

		# Return history
		return self.msg_history[self.chat_id]

	def get_history_keyboard(self):
		rows = []
		for msg in reversed(self.history()):
			rows.append([KeyboardButton(text=msg)])

		return ReplyKeyboardMarkup(
			keyboard=rows
		)

	 #####
	#     #  ####  #    # #    #   ##   #    # #####   ####
	#       #    # ##  ## ##  ##  #  #  ##   # #    # #
	#       #    # # ## # # ## # #    # # #  # #    #  ####
	#       #    # #    # #    # ###### #  # # #    #      #
	#     # #    # #    # #    # #    # #   ## #    # #    #
	 #####   ####  #    # #    # #    # #    # #####   ####

	def command_login(self, args):
		# Prepare
		if len(args) == 0:
			self.send_message('ERROR: No password was specified.')
			return

		# Login
		if args[0] == self.password:
			if self.chat_id not in self.sessions:
				self.sessions[self.chat_id] = {}

			self.sessions[self.chat_id]['password'] = args[0]
			self.send_message('*Yes sir!*')

		else:
			self.send_message('ERROR: Password is not correct.')

	def command_logout(self, args):
		if self.chat_id in self.sessions:
			self.sessions[self.chat_id] = {}

		self.send_message('You have been sucessfully logged out.')
		self.send_message('*Bye sir.*')

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
		self.telegram.sendMessage(
			self.chat_id,
			output,
			parse_mode='html',
			reply_markup=self.get_history_keyboard()
		)

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
		self.send_message(
			'Hello from TTM Trading Bot! \n'
			+ '\n'
			+ 'You can use following commands: \n'
			+ '/login password \n'
			+ '/logout \n'
			+ '/status [active/paused/-] \n'
			+ '/file filename \n'
			+ '/strategy command [arg1, [arg2, [...]]] \n'
		)
