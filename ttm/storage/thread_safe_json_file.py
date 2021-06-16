import json
from ttm.storage import Storage
import os
from pathlib import Path
import time

"""
(This file is part of TTM package)

TTM - ToTheMoon crypto trading bot

@author  Michal Mikolas (nanuqcz@gmail.com)
"""
locks = []
class ThreadSafeJSONFile(object):

	def __init__(self, file, wait_for_lock = 0.05):
		self.file = file
		# self.lock_file = "%s.lock" % self.file
		self.wait_for_lock = wait_for_lock

	def open(self, readonly = False):
		if not readonly:
			self._lock()

		# Load data
		try:
			with open(self.file, 'a+') as file:
				file.seek(0)  # a+ creates file if not exist and move the cursor to the file end
				data = json.load(file)
		except json.JSONDecodeError:
			data = {}

		# Finish
		return data

	def save(self, data):
		# Prepare directory
		directory = os.path.dirname(self.file)
		Path(directory).mkdir(parents=True, exist_ok=True)

		# Save data
		with open(self.file, 'w') as file:
			json.dump(data, file, indent=4)

		# Unlock file
		self._unlock()

	def _lock(self):
		global locks

		# Lock file: Wait for other thread to close the file
		while True:
			if self.file not in locks:
				break

			time.sleep(self.wait_for_lock)

		# Lock file: Create own lock file
		locks.append(self.file)

		# # Lock file: Wait for other thread to close the file
		# while True:
		# 	lock_exists = os.path.isfile(self.lock_file)
		# 	if not lock_exists:
		# 		break

		# 	time.sleep(self.wait_for_lock)

		# # Lock file: Create own lock file
		# with open(self.lock_file, 'w') as file:
		# 	pass

	def _unlock(self):
		global locks

		locks.remove(self.file)

		# if os.path.isfile(self.lock_file):
		# 	os.remove(self.lock_file)
