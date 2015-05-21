# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import json, re, csv

def get_fundargerd(url):
	response = requests.get(url)
	soup = BeautifulSoup(response.text)
	return soup.find(u'fundargerð').find('texti').contents[0]

def get_fundargerdir_faerslunr(thing):
	url = "http://huginn.althingi.is/altext/xml/nefndarfundir/?lthing="+str(thing)
	response = requests.get(url)
	soup = BeautifulSoup(response.text)
	nefndarfundir = {}
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
			#nefndarfundir[meeting_id]['nefnd'] = {'id': nefnd['id'], 'nafn': nefnd.contents[0]}

			#nefndarfundir[meeting_id]['dagur'] = nefndarfundur.find('dagur').contents[0]
			#nefndarfundir[meeting_id]['timi'] = nefndarfundur.find('timi').contents[0]

			fundargerd = nefndarfundur.find(u'fundargerð')
			nefndarfundir[meeting_id]['fundargerd'] = fundargerd.find('xml').contents[0]

			attendees = get_fundargerd(nefndarfundir[meeting_id]['fundargerd'])
			#find all short names (xyz)
			re.UNICODE
			attendee_short_name_list = [x[2:-1] for x in re.findall(r'\s\(.{2,20}\)', attendees.encode('utf-8'))]
			
			#TODO: compare short name list to actual MP short names | use actual short name list to search meeting minutes
			nefndarfundir[meeting_id]['short_names'] = attendee_short_name_list
		except Exception as e:
			failed.append(meeting_id)
		print "processing ", meeting_id, attendee_short_name_list
	return nefndarfundir

#get the data
data = get_fundargerdir_faerslunr(144)

#write to json
with open('nefndarfundir.js', 'w+') as outfile:
    json.dump(data, outfile)

#count short name instances
short_names = {}
for fundar_id in data:
	try:
		for short_name in data[fundar_id]['short_names']:
			if short_name in short_names:
				short_names[short_name] += 1
			else:
				short_names[short_name] = 1
	except Exception as e:
		pass

print short_names

#output csv file
with open(u'nefndarfundir.csv', 'w+') as csvfile:
    for short_name in short_names:
    	line = short_name + ',' + str(short_names[short_name]) + '\n'
    	csvfile.write(line)
