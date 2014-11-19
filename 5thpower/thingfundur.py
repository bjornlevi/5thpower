
class Thingfundur:
	def __init__(self,nafn, dags, url):
		self.nafn = nafn
		self.dags = dags
		self.url = url

	def to_json(self):
		return self.__dict__		