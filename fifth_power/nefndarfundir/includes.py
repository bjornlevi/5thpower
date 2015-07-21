# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import json, re, csv

import xmltodict

# ! --- MP INFORMATION ---
def get_mp_short_names(session):
	url = "http://www.althingi.is/altext/xml/thingmenn/?lthing="+str(session)
	response = requests.get(url)
	#print response.text.encode('utf-8', 'ignore')
	data = xmltodict.parse(response.text)

	results = []
	for mp in data[u'þingmannalisti'][u'þingmaður']:
		results.append(mp[u'skammstöfun'].encode('utf-8', 'ignore'))
	return results

def get_mp_short_names_and_id(session):
	url = "http://www.althingi.is/altext/xml/thingmenn/?lthing="+str(session)
	response = requests.get(url)
	#print response.text.encode('utf-8', 'ignore')
	data = xmltodict.parse(response.text)

	results = {}
	for mp in data[u'þingmannalisti'][u'þingmaður']:
		results[mp[u'skammstöfun'].encode('utf-8', 'ignore')] = mp[u'@id']
	return results

def get_mp_id_and_short_name(session):
	url = "http://www.althingi.is/altext/xml/thingmenn/?lthing="+str(session)
	response = requests.get(url)
	#print response.text.encode('utf-8', 'ignore')
	data = xmltodict.parse(response.text)

	results = {}
	for mp in data[u'þingmannalisti'][u'þingmaður']:
		results[mp[u'@id']] = mp[u'skammstöfun'].encode('utf-8', 'ignore')
	return results


def get_mp_commitee_membership_dates(mp_id):
	url = "http://www.althingi.is/altext/xml/thingmenn/thingmadur/nefndaseta/?nr="+str(mp_id)
	response = requests.get(url)
	#print response.text.encode('utf-8', 'ignore')
	data = xmltodict.parse(response.text)
	results = {}
	try:
		for commitee_position in data[u'þingmaður'][u'nefndasetur'][u'nefndaseta']:
			if u'út' in commitee_position[u'tímabil']:
				end = commitee_position[u'tímabil'][u'út']
			else:
				end = None		
			if commitee_position[u'þing'] in results:
				results[commitee_position[u'þing']].append({
						'commitee_id': commitee_position[u'nefnd'][u'@id'],
						'commitee_name': commitee_position[u'nefnd'][u'#text'].encode('utf-8', 'ignore'),
						'position': commitee_position[u'staða'].encode('utf-8', 'ignore'),
						'start': commitee_position[u'tímabil'][u'inn'],
						'end': end
					})
			else:
				 results[commitee_position[u'þing']] = [{
						'commitee_id': commitee_position[u'nefnd'][u'@id'],
						'commitee_name': commitee_position[u'nefnd'][u'#text'].encode('utf-8', 'ignore'),
						'position': commitee_position[u'staða'].encode('utf-8', 'ignore'),
						'start': commitee_position[u'tímabil'][u'inn'],
						'end': end
					}]
	except:
		pass
	return results

#DEPRECATE
def get_mp_commitees(session):
	#returns {commitee_id: [mp_id, ...], ...} if mp_id is not varamaður or áheyrnarfulltrúi
	url = "http://www.althingi.is/altext/xml/nefndir/nefndarmenn/?lthing="+str(session)
	response = requests.get(url)
	soup = BeautifulSoup(response.text)
	commitees = {}
	for commitee in soup.find_all('nefnd'):
		commitee_id = commitee[u'id']
		#commitee_name = u'' + commitee.find(u'heiti').contents[0].strip()
		#print commitee_id, commitee_name.encode('utf-8')
		for commitee_member in commitee.find_all(u'nefndarmaður'):
			position = commitee_member.find(u'staða').contents[0].encode('utf-8', 'ignore')
			if position == u'varamaður'.encode('utf-8', 'ignore') or position == u'áheyrnarfulltrúi'.encode('utf-8', 'ignore'):
				#ignore these positions
				pass
			else:
				if commitee_id in commitees:
					commitees[commitee_id].append(commitee_member[u'id'])
				else:
					commitees[commitee_id] = [commitee_member[u'id']]
	return commitees

# ! --- END MP INFORMATION ---

# ! --- COMMITEE INFORMATION ---

def get_commitee_members(commitee_member_lists):
	results = []
	for member_list in commitee_member_lists:
		results = results + member_list
	return list(set(results))

def get_commitee_meeting_dates(session):
	url = "http://huginn.althingi.is/altext/xml/nefndarfundir/?lthing="+str(session)
	response = requests.get(url)
	soup = BeautifulSoup(response.text)
	commitee_meeting_dates = {}
	for commitee_meeting in soup.find_all(u'nefndarfundur'):
		commitee_id = commitee_meeting.find(u'nefnd')[u'id']
		try:
			if commitee_id in commitee_meeting_dates:
				commitee_meeting_dates[commitee_id].append(commitee_meeting.find('dagur').contents[0])
			else:
				commitee_meeting_dates[commitee_id] = [commitee_meeting.find('dagur').contents[0]]
		except:
			pass
	return commitee_meeting_dates

# ! --- END COMMITEE INFORMATION ---

# ! --- MEETING INFORMATION ---

def get_meeting_minutes(url):
	response = requests.get(url)
	soup = BeautifulSoup(response.text)
	return soup.find(u'fundargerð').find('texti').contents[0]

def get_commitee_meetings_attendence(session):
	url = "http://huginn.althingi.is/altext/xml/nefndarfundir/?lthing="+str(session)
	response = requests.get(url)
	soup = BeautifulSoup(response.text)
	commitee_members_list = get_mp_short_names(session)
	mp_short_name_to_id = get_mp_short_names_and_id(session)
	results = {} #{mp_id: [[commitee_id,meeting_id], ...]}
	failed = []
	count = 0
	for commitee_meeting in soup.find_all(u'nefndarfundur'):
		try:
			#meeting information
			meeting_id = commitee_meeting[u'númer']
			commitee_id = commitee_meeting.find(u'nefnd')[u'id']
			meeting_date = commitee_meeting.find(u'dagur').contents[0]
			print "processing ", meeting_id

			#minutes information
			try:
				meeting_minutes_information = commitee_meeting.find(u'fundargerð')
				meeting_minutes = get_meeting_minutes(meeting_minutes_information.find('xml').contents[0])
			except:
				print "meeting mintues do not include attendence in this session"
				exit()

			
			#attendee list
			re.UNICODE
			raw_short_names = [x[2:-1] for x in re.findall(r'\s\(.{2,20}\)', meeting_minutes.encode('utf-8'))]
			
			#clean short name list
			short_name_list = []
			for short_name in raw_short_names:
				if short_name in commitee_members_list:
					short_name_list.append(short_name)

			#log attendence: mp, meeting_id
			for mp in short_name_list:
				mp_id = mp_short_name_to_id[mp]
				if mp_id in results:
					results[mp_id].append([commitee_id, meeting_id, meeting_date])
				else:
					results[mp_id] = [[commitee_id, meeting_id, meeting_date]]
		except Exception as e:
			print str(e)
			failed.append(meeting_id)
	return results

# ! --- END MEETING INFORMATION ---
