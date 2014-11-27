import json

class Thingmadur:
	
	def __init__(self, nafn, skammstofun, url):
		self.nafn = nafn
		self.skammstofun = skammstofun
		self.url = url
		self.party = []
		self.thing = []

	def add_party(self, party):
		self.party.append(party)

	def add_thing(self, thing):
		self.thing.append(thing)

	def to_json(self):
		return self.__dict__