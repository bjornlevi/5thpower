# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import re

from pymongo import MongoClient, Connection

connection_name = "althingi"
mp_collection = "mps"
connection = Connection()
db = connection[connection_name]
query_path = "http://www.althingi.is"

def get_mp_id(name):
	collection = db[mp_collection]
	return collection.find({"name": name.strip()})

def get_absents(url):
	response = requests.get(url)
	soup = BeautifulSoup(response.text)
	results = []
	for absent in soup('p'):
		name = absent.text.split(',')[0]
		#bug for Birkir J. Jonnson
		if name == u"Birkir J. Jónsson":
			name = u"Birkir Jón Jónsson"
		#but for Kristín Ástgeirsgóttir
		if name == u"Kristín Ástgeirsgóttir":
			name = u"Kristín Ástgeirsdóttir"
		mp = get_mp_id(name)
		minister = False
		i = 1
		while mp.count() == 0 and i <= len(name.split(' ')):
			#minister, contains no ',' - must try finding name incrementally
			mp = get_mp_id(' '.join(name.split(' ')[0:i]))
			minister = ' '.join(name.split(' ')[i:])
			i += 1
		try:
			results.append({'mp_id': mp[0]['mp_id'], 'minister': minister})
		except:
			print "error", absent, name
	return results

def collect_meetings(session_nr):
	response = requests.get('http://www.althingi.is/dba-bin/fulist.pl?ltg='+session_nr)
	soup = BeautifulSoup(response.text)
	meetings = soup.find_all(href=re.compile('/altext/'))
	results = []
	for meeting in meetings:
		if "fundur" in meeting.text or "setning" in meeting.text:
			results.append(str(int(meeting['href'].split('/')[-1][1:4])))
	return results

def collect_absents(session_nr, meeting_nr):
	try:
		meeting_nr = '00'+meeting_nr
		response = requests.get('http://www.althingi.is/altext/'+session_nr+'/f'+meeting_nr[-3:]+'.sgml')
		soup = BeautifulSoup(response.text)
		is_fjarvist = soup.find(text="Fjarvistarleyfi")
		if is_fjarvist:
			return get_absents(is_fjarvist.parent.parent['href'])
		else:
			return []
	except Exception as e:
		print e
		print session_nr, meeting_nr
		return []

def collect_all_absents():
	response = requests.get('http://www.althingi.is/vefur/altutg.html')
	soup = BeautifulSoup(response.text)
	things = soup.find_all(href=re.compile('/dba-bin/fulist.pl'))

	by_thing = {}

	for thing in things[1:]:
		print thing.text
		by_thing[thing.text] = {}
		response = requests.get(query_path + thing['href'])
		soup = BeautifulSoup(response.text)
		fundir = soup.find_all(href=re.compile('/altext/'))
		for fundur in fundir:
			if "fundur" in fundur.text or "setning" in fundur.text:
				fundur_key = fundur.text.replace('.','')
				try:
					by_thing[thing.text][fundur_key] = find_absents(query_path + fundur['href'])
				except:
					pass
			#print fundur_name, fundur_link
		#f = open(thing.text, 'w')
		#f.write(str(by_thing[thing.text]))
		#by_thing = {}
	#return by_thing
