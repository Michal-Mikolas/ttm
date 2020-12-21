import json
from ttm.storage import Storage

class JSONFile(Storage):

	def __init__(self, file):
		self.file = file
		self.data = None

		try:
			self._reload()
		except:
			self.data = {}
			self._resave()
			self._reload()

	def get(self, key):
		if self.data == None:
			self._reload()

		if key not in self.data:
			return None

		return self.data[key]

	def save(self, key, value):
		self.data[key] = value
		self._resave()

	def delete(self, key):
		self.data.pop(key, None)
		self._resave()

	###
	 #  #    # ##### ###### #####  #    #   ##   #
	 #  ##   #   #   #      #    # ##   #  #  #  #
	 #  # #  #   #   #####  #    # # #  # #    # #
	 #  #  # #   #   #      #####  #  # # ###### #
	 #  #   ##   #   #      #   #  #   ## #    # #
	### #    #   #   ###### #    # #    # #    # ######

	def _reload(self):
		with open(self.file, 'a+') as file:
			file.seek(0)  # a+ creates file if not exist and move the cursor to the file end
			self.data = json.load(file)

	def _resave(self):
		with open(self.file, 'w') as file:
			json.dump(self.data, file, indent=4)
