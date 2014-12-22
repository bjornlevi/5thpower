#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import re

def get_sessions():
	response = requests.get("http://www.althingi.is/vefur/altutg.html")
	soup = BeautifulSoup(response.text)
	sessions = soup.find_all(href=re.compile("/dba-bin/fulist.pl\?ltg="))
	query_path = "http://www.althingi.is"
	session_data = []
	for session in sessions:
		try:
			int(session['href'].split('ltg=')[-1]) #only allow numbered sessions
			session_data.append({'session_nr': session['href'].split('ltg=')[-1], 'session_url': query_path + session['href']})
		except:
			pass
	return session_data

def get_party_info():
	"""
	returns a list of party information from althingi.is web
	[{url:'path to party members', 'party_id': 'party short letter'}, {}, ...]
	"""
	response = requests.get('http://www.althingi.is/vefur/thingfl.html')
	soup = BeautifulSoup(response.text)
	parties = soup.find_all(href=re.compile("/dba-bin/thmn.pl"))
	query_path = "http://www.althingi.is"

	results = []

	#cycle through political parties
	for party in parties:
		try:
			#get party letter and url
			party_id = party.text
			party_url = party['href']

			#special for current parties
			if party_id == u'Þingmenn flokksins':
				#add to the url and remove the time variable
				party_url = query_path + party['href']
				party_url = party_url.replace('timi=.', '') #remove timi to get all mps for this party
				#get party_id
				party_id = re.search('thingfl=(.*)&', party_url).group(1)
			elif len(party_id) > 6:
				continue #ignore stjorn þingflokksins
			results.append({'party_url': party_url, 'party_id': party_id})
		except:
			pass
	return results	

def get_party_description():
	"""
	returns a list of party information from althingi.is web
	[{'party_name':'Einhverflokkur', 'party_id': 'party short letter'}, {}, ...]
	"""
	response = requests.get('http://www.althingi.is/vefur/thingfl.html')
	soup = BeautifulSoup(response.text)
	parties = soup.find_all(href=re.compile("/dba-bin/thmn.pl"))
	query_path = "http://www.althingi.is"

	results = []

	#cycle through political parties
	for party in parties:
		try:
			#get party letter and url
			party_id = party.text
			party_name = party.parent.parent.find("span").text
			#special for current parties
			if party_id == u'Þingmenn flokksins':
				party_name = party.parent.parent.parent.a.text
				#add to the url and remove the time variable
				party_url = query_path + party['href']
				party_url = party_url.replace('timi=.', '') #remove timi to get all mps for this party
				#get party_id
				party_id = re.search('thingfl=(.*)&', party_url).group(1)
			elif len(party_id) > 6:
				continue #ignore stjorn þingflokksins
			results.append({'party_name': party_name, 'party_id': party_id})
		except:
			pass
	return results		

def get_session_absents(session_nr):
	session_absents = []
	for meeting_nr in read_absents.collect_meetings(session_nr):
		for meeting_absents in read_absents.collect_absents(session_nr, meeting_nr):
			session_absents.append({
					'session_nr': session_nr,
					'meeting_nr': meeting_nr,
					'mp_id': meeting_absents['mp_id'],
					'minister': meeting_absents['minister']
				})	
	return session_absents