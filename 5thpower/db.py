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
	collection_name = "votes"

	def __init__(self):
		self.connection = Connection()
		self.db = self.connection[self.connection_name]

	def is_vote(self, vote_id):
		response = requests.get('http://www.althingi.is/dba-bin/atkvgr.pl?nnafnak='+str(vote_id))
		soup = BeautifulSoup(response.text)
		nobrs = soup.find_all('nobr')
		if len(nobrs)==0:
			return False
		return True

	def vote_exists(self, vote_id):
		collection = self.db[self.collection_name]
		if collection.find_one({"vote_id": vote_id}):
			return True
		return False

	def collect_votes(self, current):
		results = []
		try:
			while current.nextSibling.name != 'h2':
				current = current.nextSibling
				if current.name == 'nobr':
					results.append(current.text)
		except:
			pass
		return results

	def get_data(self, vote_id):
		if not self.is_vote(vote_id):
			print "Vote: " + str(vote_id) + " skipped"
			return False

		if self.vote_exists(vote_id):
			print "Vote: " + str(vote_id) + " exists"
			return False

		print "Running vote: " + str(vote_id)
		response = requests.get('http://www.althingi.is/dba-bin/atkvgr.pl?nnafnak='+str(vote_id))
		soup = BeautifulSoup(response.text)
		print "Parsing vote: " + str(vote_id)
		#<h2 class="FyrirsognSv">já:</h2>
		#<h2 class="FyrirsognSv">nei:</h2>
		#<h2 class="FyrirsognSv">greiðir ekki atkvæði:</h2>
		#<h2 class="FyrirsognSv">fjarvist:</h2>

		vote = {"vote_id": vote_id}
		#add more fields (url, date)

		#collect votes
		for header in soup.find_all('h2'):
			if header.text == u'já:':
				#handle yes
				vote['yes'] = self.collect_votes(header)
			elif header.text == u'nei:':
				#handle no
				vote['no'] = self.collect_votes(header)
			elif header.text == u'greiðir ekki atkvæði:':
				#handle no vote
				vote['abstain'] = self.collect_votes(header)
			elif header.text == u'fjarvist:':
				#handle absent
				vote['absent'] = self.collect_votes(header)
		print "Saving vote: " + str(vote_id)
		return cherrypy.engine.publish('db-save', vote)

	def save(self, data):
		collection = self.db[self.collection_name]
		results = ""
		try:
			insert_id = collection.insert(data)
		except Exception as e:
			return dumps({"error": e})
		return dumps({"success": str(insert_id)})


	def update(self, update_id, data):
		collection = self.db[self.collection_name]
		return collection.update({"_id": ObjectId(str(update_id))},{"$set": data}, upsert = True)

	def delete(self, data):
		"""
			data = {"column": "find data", ...}
		"""
		collection = self.db[self.collection_name]
		results = []

		for k in data.keys():
			if k == '_id':
				data[k] = ObjectId(str(data[k]))

		collection.remove(data)

	def get(self, order_id):
		collection = self.db[self.collection_name]
		results = []
		for i in collection.find({"_id": ObjectId(str(order_id))}):
			i["_id"] = str(i["_id"])
			results.append(i)
		return results

	def get_where(self, data):
		"""
			data = {"column": "find data", ...}
		"""
		collection = self.db[self.collection_name]
		results = []

		for k in data.keys():
			if k == '_id':
				data[k] = ObjectId(str(data[k]))

		for i in collection.find(data):
			i["_id"] = str(i["_id"])
			results.append(i)
		return results

	def get_all(self):
		collection = self.db[self.collection_name]
		results = []
		for i in collection.find():
			i["_id"] = str(i["_id"])
			results.append(i)
		return results