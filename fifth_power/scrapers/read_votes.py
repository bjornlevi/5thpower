#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient, Connection

connection_name = "althingi"
vote_collection = "votes"
mp_collection = "mps"
connection = Connection()
db = connection[connection_name]

def vote_exists(vote):
	collection = db[vote_collection]
	if collection.find({'nafnak': vote['nafnak'], 'voter': vote['voter']}).count() > 0:
		return True
	return False

def insert_vote(vote):
	collection = db[vote_collection]
	try:
		insert_id = collection.insert(vote)
		return insert_id
	except Exception as e:
		return "error"

def get_mp_votes_for_thing(current_mp, thing):
	response = requests.get('http://www.althingi.is/dba-bin/atkvaedaskra.pl?lthing='+thing+'&thmsk='+current_mp)
	soup = BeautifulSoup(response.text)
	all_votes = soup.find_all("div", class_= "AlmTexti")
	return all_votes[0].find_all("tr")

def get_vote_data(vote_data, current_mp, thing, mal_nr):
	vote = vote_data.find_all("td")
	if len(vote) != 4:
		return #not a vote, go to the next row

	#get vote data
	vote_results = {}
	vote_results['voter'] = current_mp
	vote_results['thing'] = thing
	vote_results['mal'] = mal_nr
	vote_results['date'] = vote[0].nobr.text.strip()
	vote_results['phase'] = vote[1].text.strip()
	try:
		vote_results['type'] = vote[2].abbr['title'].strip()
	except:
		vote_results['type'] = vote[2].a.text.strip()
	vote_results['nafnak'] = vote[2].a['href'].split('=')[-1].strip()
	vote_results['vote'] = vote[3].font.text
	return vote_results

def collect_votes():
	#http://www.althingi.is/dba-bin/atkvaedaskra.pl?lthing=144&thmsk=HHG
	"""
	{
		{
			'voter': 'mp_skammstofun',
			'thing': 'thing nr',
			'mal': 'thingmal',
			'date': '24.11.2006 10:49'
			'nafnak_nr': 1234, 
			'type': 'frumvarp/tillaga/...'
			'phase': '1. umræða/2. umræða/3. umræða/...'
			'vote': 'já/greiðir ekki atkvæði/nei/fjarvist/fjarverandi'}
		}

	}
	"""
	vote_results = {}
	failed_votes = []
	mps = db[mp_collection]
	for i,mp in enumerate(mps.find()[800:]):
		print i+800
		current_mp = mp['skammstofun']
		for thing in mp['thing']:
			print thing, current_mp
			mal_nr = ''
			insert_votes = []
			for tr in get_mp_votes_for_thing(current_mp, thing):
				try:
					#get mal_nr
					try:
						mal_nr = tr.td.h2.a['href'].split('=')[-1]
						continue #done with this row, continue the next row
					except:
						pass

					#get vote data, can return None if it is not a valid vote
					vote = get_vote_data(vote_data, current_mp, thing, mal_nr)
					#add vote to bulk insert list
					if vote:
						insert_votes.append(vote)
				except Exception as e:
					pass

			#bulk insert collected votes		
			if insert_vote(insert_votes) == "error":
				failed_votes.append({'mp': current_mp, 'thing': thing})

	
