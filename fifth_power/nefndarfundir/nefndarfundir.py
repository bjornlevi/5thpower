# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import json, re, csv

import xmltodict

# ! --- MP INFORMATION ---
def get_mp_short_names(thing):
	url = "http://www.althingi.is/altext/xml/thingmenn/?lthing="+str(thing)
	response = requests.get(url)
	#print response.text.encode('utf-8', 'ignore')
	data = xmltodict.parse(response.text)

	results = []
	for mp in data[u'þingmannalisti'][u'þingmaður']:
		results.append(mp[u'skammstöfun'].encode('utf-8', 'ignore'))
	return results

def get_mp_short_names_and_id(thing):
	url = "http://www.althingi.is/altext/xml/thingmenn/?lthing="+str(thing)
	response = requests.get(url)
	#print response.text.encode('utf-8', 'ignore')
	data = xmltodict.parse(response.text)

	results = {}
	for mp in data[u'þingmannalisti'][u'þingmaður']:
		results[mp[u'skammstöfun'].encode('utf-8', 'ignore')] = mp[u'@id']
	return results	

def get_mp_commitees(thing):
	url = "http://www.althingi.is/altext/xml/nefndir/nefndarmenn/?lthing="+str(thing)
	response = requests.get(url)
	soup = BeautifulSoup(response.text)
	commitees = {}
	for commitee in soup.find_all('nefnd'):
		commitee_id = commitee[u'id']
		#commitee_name = u'' + commitee.find(u'heiti').contents[0].strip()
		#print commitee_id, commitee_name.encode('utf-8')
		for commitee_member in commitee.find_all(u'nefndarmaður'):
			position = commitee_member.find(u'staða').contents[0].encode('utf-8', 'ignore')
			if position == u'varamaður'.encode('utf-8', 'ignore') or position == u'áheynarfulltrúi'.encode('utf-8', 'ignore'):
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

def get_commitee_meeting_dates(thing):
	url = "http://huginn.althingi.is/altext/xml/nefndarfundir/?lthing="+str(thing)
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

def get_commitee_meetings_attendence(thing):
	url = "http://huginn.althingi.is/altext/xml/nefndarfundir/?lthing="+str(thing)
	response = requests.get(url)
	soup = BeautifulSoup(response.text)
	commitee_members_list = get_mp_short_names(thing)
	mp_short_name_to_id = get_mp_short_names_and_id(thing)
	results = {} #{mp_id: [[commitee_id,meeting_id], ...]}
	failed = []
	count = 0
	for commitee_meeting in soup.find_all(u'nefndarfundur'):
		try:
			#meeting information
			meeting_id = commitee_meeting[u'númer']
			commitee_id = commitee_meeting.find(u'nefnd')[u'id']

			#minutes information
			meeting_minutes_information = commitee_meeting.find(u'fundargerð')
			meeting_minutes = get_meeting_minutes(meeting_minutes_information.find('xml').contents[0])
			
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
					results[mp_id].append([commitee_id, meeting_id])
				else:
					results[mp_id] = [[commitee_id, meeting_id]]
		except Exception as e:
			failed.append(meeting_id)
		print "processing ", meeting_id, short_name_list
	return results

# ! --- END MEETING INFORMATION ---
 

# ! --- SAVE OUTPUT ---

print "Processing commitee members"
commitee_membership = get_mp_commitees(144)
commitee_members = get_commitee_members([commitee_membership[i] for i in commitee_membership])

print "Saving commitee membership"

#mps registered as commitee members
with open('mps_in_commitees.csv', 'w+') as csvfile:
	data = ""
	for member in commitee_members:
		data += member.encode('utf-8', 'ignore') + '\n'
	csvfile.write(data)

#mps registered as commitee members
with open('commitee_members.csv', 'w+') as csvfile:
	data = ""
	for commitee in commitee_membership:
		for member in commitee_membership[commitee]:
			data += commitee.encode('utf-8', 'ignore') + "," + member.encode('utf-8', 'ignore') + '\n'
	csvfile.write(data)

print "Processing meeting attendence"

#count number of meetings in each commitee
mp_meetings = get_commitee_meetings_attendence(144)
with open('commitee_attendence.csv', 'w+') as csvfile:
	data = ""
	for mp in mp_meetings:
		#for meeting in mp_meetings[mp]: #to list all meetings attended
			#mp, commitee_id, meeting_id
			#data += mp + ',' + str(meeting[0]) + ',' + str(meeting[1]) + '\n'
		#mp, number of meetings
		data += mp + ',' + str(len(mp_meetings[mp])) + '\n' #to only count number of meetings for each mp
	csvfile.write(data)

print "processing commitee meeting count"

#count number of meetings for each commitee
commitee_meetings = get_commitee_meeting_dates(144)
with open('commitee_meetings.csv', 'w+') as csvfile:
	data = ""
	for meeting in commitee_meetings:
		data += meeting.encode('utf-8', 'ignore') + "," + str(len(commitee_meetings[meeting])) + '\n'
	csvfile.write(data)