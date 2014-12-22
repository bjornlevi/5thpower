#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pymongo import MongoClient, Connection
from scrapers import read_fjarvistir, read_votes, read_mps, read_parties, read_sessions, read_absents
import utility

import sys

connection_name = "althingi"
absent_collection = "absents"
mp_collection = "mps"
session_collection = "sessions"
party_collection = "parties"
connection = Connection()
db = connection[connection_name]

def mp_exists(mp_id):
	collection = db[mp_collection]
	if collection.find_one({"nafnak": mp_id}):
		return True
	return False

def session_exists(session_nr):
	collection = db[session_collection]
	if collection.find_one({"session_nr": session_nr}):
		return True
	return False	

def insert(data, data_collection):
	collection = db[data_collection]
	try:
		insert_id = collection.insert(data)
		return True
	except Exception as e:
		print e #return dumps({"error": e})
		return False

def update_mp(mp):
	collection = db[mp_collection]
	try:
		insert_id = collection.insert({
			"short_name": mp.short_name,
			"name": mp.name,
			"mp_id": mp.mp_id,
			"sessions": mp.sessions,
			"deputy": mp.deputy,
			"image_url": mp.image_url
		 })
	except Exception as e:
		print e #return dumps({"error": e})
		return

def update_new_session(session_nr):

	#update absents
	session_absents = utility.get_session_absents(session_nr)
	insert(session_absents, absent_collection)

def update_data():
	if len(sys.argv) == 1: #should be 0 = file name, 1 = session
		print "Provide session number"
		return
	session_nr = sys.argv[1]

	if not session_exists(session_nr):
		#session does not exist, update the sessions to check if a new session has started
		new_session = read_sessions.get_session(session_nr)
		if new_session:
			insert(new_session)
		else:
			print "Session does not exist at althingi.is"
			return

		print "Updating new session", session_nr
		update_new_session(session_nr)

	update_existing_session(session_nr)


update_data()