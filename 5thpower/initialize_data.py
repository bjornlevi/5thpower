#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pymongo import MongoClient, Connection
from scrapers import read_fjarvistir, read_votes, read_thingmenn

connection_name = "althingi"
fjarvistir_collection = "absents"
thingmenn_collection = "mps"
connection = Connection()
db = connection[connection_name]

def thingmadur_exists(thingmadur):
	collection = db[thingmenn_collection]
	if collection.find_one({"skammstofun": thingmadur}):
		return True
	return False

def thingfundur_exists(thing, fundur):
	collection = db[fjarvistir_collection]
	if collection.find_one({"$and": [{"thing": {"$regex": thing[0:3]}}, {"fundur": fundur}]}):
		return True
	return False	

def insert_fjarvist(thing, data):
	collection = db[fjarvistir_collection]
	for fundur in data:
		if thingfundur_exists(thing, fundur):
			print "Thingfundur exists", thing, fundur
			continue
		try:
			insert_id = collection.insert({"thing": thing, "fundur": fundur, "absent": data[fundur]})
		except Exception as e:
			print e #return dumps({"error": e})
			return


def insert_thingmadur(thingmadur):
	print thingmadur.to_json()

def initialize_data():
	#for vote_id in range(10):
		#read votes updated the database on it's own
	#	print read_votes.collect_votes(vote_id)

	fjarvist_data = read_fjarvistir.collect_fjarvistir()
	for thing in fjarvist_data:
		insert_fjarvist(thing, fjarvist_data[thing])
	
	#thingmadur_data = read_thingmenn.collect_thingmenn()		
	#for thingmadur in thingmadur_data:
	#	insert_thingmadur(thingmadur_data[thingmadur])

initialize_data()