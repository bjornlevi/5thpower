#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pymongo import MongoClient, Connection
import sys
from bson.objectid import ObjectId
import cherrypy
import requests
from bs4 import BeautifulSoup

from json import dumps
class DB(object):

	connection_name = "althingi"
	vote_collection = "votes"
	mp_collection = "mps"
	absent_collection = "absents"
	session_collection = "sessions"

	def __init__(self):
		self.connection = Connection()
		self.db = self.connection[self.connection_name]

	def get_votes(self, session_nr):
		collection = self.db[self.vote_collection]
		results = []
		for i in collection.find({"session_nr": session_nr}):
			i["_id"] = str(i["_id"])
			results.append(i)
		return results

	def get_mps(self, session_nr):
		collection = self.db[mp_collection]
		results = []
		for i in collection.find({"session_nr": session_nr}):
			i["_id"] = str(i["_id"])
			i["nafn"] = i["nafn"]
			results.append(i)
		return results

	def get_absents(self):
		sessions = self.db[self.session_collection]
		absents = self.db[self.absent_collection]
		results = []
		for session in sessions.find():
			results.append({
				session['session_nr']: absents.find({'session_nr': session['session_nr']}).count()
				})
		return results

	def get_vote_options(self, session):
		votes = self.db[self.vote_collection]
		return votes.distinct('vote')