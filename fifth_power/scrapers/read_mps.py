#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import re
from models.mp import MP
from utility import get_party_info
#print response.text.encode('utf-8')

def get_member_list(url):
	response = requests.get(url)
	soup = BeautifulSoup(response.text)
	return soup.find(id="t_thingmenn").find_all('tr')

def get_member_info(member, party_id):
	try:
		cols = member.find_all('td')
		session = member.td.text
		name = cols[1].a.text
		short_name = re.search('\(.*\)', str(cols[1])).group()[1:-1]
		#fix for empty short_name 
		#	/ for some strange reason it's not missing on the page but it's missing in the soup
		if short_name == '':
			short_name = 'HerdÞ'
		
		mp_id =  cols[1].a['href'].split("=")[-1]

		t = MP(name.strip(), short_name.strip(), mp_id, get_mp_image_url(mp_id))
		t.add_session({session: party_id})
		#check if deputy MP
		if u"varamaður" in cols[1].text:
			deputy_for = cols[1].find_all("a")[1]["href"].split("=")[-1]
			t.add_deputy(session, deputy_for)	
		return t
	except Exception as e:
		return None

def update_mp_entry(entry, mp, party_id, session):
	entry.add_session({session: party_id})
	if mp.deputy:
		entry.add_deputy(session, mp.deputy[session])
	return entry

def get_mp_image_url(mp_id):
	return 'http://www.althingi.is/myndir/mynd/thingmenn/'+mp_id+'/org/mynd.jpg'

def collect_mps():
	"""
		Read the althing.is vefur and returns a dictionary of all parliamentarians by their short by_short_names
		{
			'short_name': {
				'name': 'Someone Someson',
				'short_name': 'SS',
				'mp_id': 234
				'url': 'althingi.is/url/to/parliamentarian',
				'party': [{'session_nr': party_id}, {...}, ...],
				'img_url': get_mp_image_url(mp_id)
			},
			...

		}
	"""
	response = requests.get('http://www.althingi.is/vefur/thingfl.html')
	soup = BeautifulSoup(response.text)
	query_path = "http://www.althingi.is"

	by_mp_id = {}

	#members of parliament
	parties = get_party_info()
	for party in parties:
		party_url = party['party_url']
		party_id = party['party_id']
		print "Getting member info for", party_id
		#get all party members - ever
		member_list = get_member_list(party_url)
		
		print "Found", len(member_list), "entries"
		#cycle through all party members
		for member in member_list:
			member_info = get_member_info(member, party_id)
			if member_info:
				#if MP already exists, update
				if member_info.mp_id in by_mp_id:
					print "Updating", member_info.short_name
					#MP already added, add thing and possibly a new party or deputy
					by_mp_id[member_info.mp_id] = update_mp_entry(by_mp_id[member_info.mp_id], member_info, party_id, member_info.sessions[-1].keys()[0])
				else:
					#add new
					print "Adding", member_info.short_name
					by_mp_id[member_info.mp_id] = member_info

	return by_mp_id