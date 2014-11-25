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

	def is_vote(self, soup):
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
					#results.append(self.get_thingmadur(current.text))
		except:
			pass
		return results

	def get_votes(self, vote_id):
		response = requests.get('http://www.althingi.is/dba-bin/atkvgr.pl?nnafnak='+str(vote_id))
		soup = BeautifulSoup(response.text)

		if not self.is_vote(soup):
			print "Vote: " + str(vote_id) + " skipped"
			return False

		if self.vote_exists(vote_id):
			print "Vote: " + str(vote_id) + " exists"
			return False

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
		self.collection_name = 'votes'
		return cherrypy.engine.publish('db-save', vote)

	def get_thingmadur(self, name):
		collection = self.db['thingmenn']
		results = []
		for i in collection.find({"nafn": name}):
			i["_id"] = str(i["_id"])
			results.append(i)
		return results		

	def get_thingmenn(self):
		self.collection_name = 'thingmenn'
		results = []
		letters = ['A','%C1','B','D','E','F','G','H','I','%CD','J','K','L','M','N','O','%D3','P','R','S','T','U','V','W','%DE','%D6']
		for letter in letters:
			response = requests.get('http://www.althingi.is/altext/cv/is/?cstafur='+str(letter))
			soup = BeautifulSoup(response.text)
			print "Parsing page: " + soup.title.text
			for li in soup.find_all('li'):
				thingmadur = {
					'nafn': li.a.text,
					'url': li.a['href']
				}
				results.append(cherrypy.engine.publish('db-save', thingmadur))
		return results


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