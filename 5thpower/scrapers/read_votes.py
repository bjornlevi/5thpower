#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient, Connection

connection_name = "althingi"
collection_name = "votes"
connection = Connection()
db = connection[connection_name]

def is_vote(soup):
	nobrs = soup.find_all('nobr')
	if len(nobrs)==0:
		return False
	return True

def vote_exists(vote_id):
	collection = db[collection_name]
	if collection.find_one({"vote_id": vote_id}):
		return True
	return False

def get_votes(current):
	results = []
	try:
		while current.nextSibling.name != 'h2':
			current = current.nextSibling
			if current.name == 'nobr':
				results.append(current.text)
				#results.append(get_thingmadur(current.text))
	except:
		pass
	return results

def collect_votes(vote_id):
	response = requests.get('http://www.althingi.is/dba-bin/atkvgr.pl?nnafnak='+str(vote_id))
	soup = BeautifulSoup(response.text)

	if not is_vote(soup):
		return "Vote: " + str(vote_id) + " skipped"

	if vote_exists(vote_id):
		return "Vote: " + str(vote_id) + " exists"

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
			vote['yes'] = get_votes(header)
		elif header.text == u'nei:':
			#handle no
			vote['no'] = get_votes(header)
		elif header.text == u'greiðir ekki atkvæði:':
			#handle no vote
			vote['abstain'] = get_votes(header)
		elif header.text == u'fjarvist:':
			#handle absent
			vote['absent'] = get_votes(header)
	print "Saving vote: " + str(vote_id)
	collection_name = 'votes'
	return cherrypy.engine.publish('db-save', vote)