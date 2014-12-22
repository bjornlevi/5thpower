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

def mp_exists(mp):
	collection = db[mp_collection]
	if collection.find_one({"skammstofun": mp}):
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


def insert_mp(mp):
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

def initialize_data():
	if len(sys.argv) == 1:
		print "initialize 'mps', 'sessions', 'votes', 'absents' or 'parties'"
		return

	if sys.argv[1] == 'mps':
		mp_data = read_mps.collect_mps()		
		for mp in mp_data:
			insert_mp(mp_data[mp])

	if sys.argv[1] == 'sessions':
		session_data = read_sessions.collect_sessions()
		insert(session_data, session_collection)

	if sys.argv[1] == 'votes':
		#for all mps in system, collect their votes and save to votes collection
		read_votes.collect_votes()

	if sys.argv[1] == 'absents':
		collection = db[session_collection]
		for session in collection.find():#range(123, 124):
			session_nr = session['session_nr']
			print "Processing session nr", session_nr
			session_absents = utility.get_session_absents(session_nr)
			insert(session_absents, absent_collection)

	if sys.argv[1] == 'parties':
		party_data = read_parties.collect_parties()
		insert(party_data, party_collection)	

initialize_data()