#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pymongo import MongoClient, Connection

class Absent:
	connection_name = "althingi"
	absent_collection = "absents"

	def __init__(self, session_nr, meeting_nr):
		self.session_nr = session_nr
		self.meeting_nr = meeting_nr
		self.connection = Connection()
		self.db = connection[self.connection_name]
		self.absents = self.get_absents(session_nr, meeting_nr)

	def get_absents(self, session_nr, meeting_nr):
		collection = self.db[absent_collection]
		results = []
		absents = collection.find({'session_nr': session_nr, 'meeting_nr': meeting_nr})
		if absents.count() > 0:
			for absent in absents:
				results.append(absent)
		else:
			return []
		return results

	def save(self):
		pass

	def to_json(self):
		return self.__dict__
