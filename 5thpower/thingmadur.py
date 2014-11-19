import json

class Thingmadur:
	
	def __init__(self, nafn, skammstofun, titill, url, kjordaemi):
		self.nafn = nafn
		self.skammstofun = skammstofun
		self.titill = titill
		self.url = url
		self.kjordaemi = kjordaemi

	def to_json(self):
		return self.__dict__