# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import json, re, csv

def get_fundargerd(url):
	response = requests.get(url)
	soup = BeautifulSoup(response.text)
	return soup.find(u'fundargerð').find('texti').contents[0]

def get_meeting_dates(thing):
	url = "http://huginn.althingi.is/altext/xml/nefndarfundir/?lthing="+str(thing)
	response = requests.get(url)
	soup = BeautifulSoup(response.text)
	meeting_dates = []
	for nefndarfundur in soup.find_all(u'nefndarfundur'):
		try: 
			meeting_dates.append(nefndarfundur.find('dagur').contents[0])
		except:
			pass
	return meeting_dates

def get_fundargerdir_faerslunr(thing):
	url = "http://huginn.althingi.is/altext/xml/nefndarfundir/?lthing="+str(thing)
	response = requests.get(url)
	soup = BeautifulSoup(response.text)
	nefndarfundir = {}
	attending_days = {}
	failed = []
	count = 0
	for nefndarfundur in soup.find_all(u'nefndarfundur'):
		try: 
			meeting_id = nefndarfundur[u'númer']
			nefndarfundir[meeting_id] = {}

			#extra info fields if wanted
			#dagskra = nefndarfundur.find(u'dagskrá')
			#nefndarfundir[meeting_id]['dagskra'] = nefndarfundur.find('xml').contents[0]

			#nefnd = nefndarfundur.find('nefnd')
			#nefndarfundir[meeting_id]['nefnd'] = nefnd['id']#{'id': nefnd['id'], 'nafn': nefnd.contents[0]}

			#nefndarfundir[meeting_id]['dagur'] = nefndarfundur.find('dagur').contents[0]
			#nefndarfundir[meeting_id]['timi'] = nefndarfundur.find('timi').contents[0]

			fundargerd = nefndarfundur.find(u'fundargerð')
			nefndarfundir[meeting_id]['fundargerd'] = fundargerd.find('xml').contents[0]

			attendees = get_fundargerd(nefndarfundir[meeting_id]['fundargerd'])
			#find all short names (xyz)
			re.UNICODE
			attendee_short_name_list = [x[2:-1] for x in re.findall(r'\s\(.{2,20}\)', attendees.encode('utf-8'))]
			
			dagur = nefndarfundur.find('dagur').contents[0]
			for attendee in attendee_short_name_list:
				if attendee in attending_days:
					attending_days[attendee].append(dagur)
				else:
					attending_days[attendee] = [dagur]

			#TODO: compare short name list to actual MP short names | use actual short name list to search meeting minutes
			#nefndarfundir[meeting_id]['short_names'] = attendee_short_name_list

		except Exception as e:
			failed.append(meeting_id)
		print "processing ", meeting_id, attendee_short_name_list
	return attending_days

#data = get_meeting_dates(144)

#get the data
data = get_fundargerdir_faerslunr(144)

"""
#write to json
with open('nefndarfundir.js', 'w+') as outfile:
    json.dump(data, outfile)

#count short name instances
short_names = {}
meetings_attended = {}
for meeting_id in data:
	try:
		for short_name in data[meeting_id]['short_names']:
			if short_name in short_names:
				short_names[short_name] += 1
			else:
				short_names[short_name] = 1
			if short_name in meetings_attended:
				meetings_attended[short_name].append(data[meeting_id]['nefnd'])
			else:
				meetings_attended[short_name] = [data[meeting_id]['nefnd']]
	except Exception as e:
		pass

with open(u'meeting_dates.csv', 'w+') as csvfile:
    for key in data:
    	line = "'" + key + "':" + str(data[key]) + ',\n'
    	csvfile.write(line)
"""
#output csv file
with open(u'nefndarfundir.csv', 'w+') as csvfile:
    for short_name in data:
    	line = short_name + ',' + str(len(data[short_name])) + '\n'
    	csvfile.write(line)
