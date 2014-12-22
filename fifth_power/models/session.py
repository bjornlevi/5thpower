#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pymongo import MongoClient, Connection

class Session:
	
	connection_name = "althingi"
	session_collection = "sessions"
	mp_collection = "mps"
	
	session_nr = ''

	def __init__(self, session_nr):
		self.session_nr = session_nr
		self.connection = Connection()
		self.db = connection[self.connection_name]
		self.meetings = self.get_meetings(session_nr)
		self.mps = self.get_mps(session_nr)

	def get_mps(self, session_nr):
		collection = self.db[mp_collection]
		results = []
		for mp in collection.find({'session_nr': session_nr}):
			results.append(mp)
		return results

	def save(self):
		pass

	def to_json(self):
		return {
			'session_nr': self.session_nr,
			'mps': self.meetings
		}