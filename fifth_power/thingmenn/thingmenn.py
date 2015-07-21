# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import json, re, csv

def get_fundargerd(url):
	response = requests.get(url)
	soup = BeautifulSoup(response.text)
	return soup.find(u'fundargerð').find('texti').contents[0]

def get_mps(session):
	url = "http://www.althingi.is/altext/xml/thingmenn/?lthing="+str(session)
	response = requests.get(url)
	response_text = response.text.replace(u'<þ', '<th')
	response_text = response_text.replace(u'</þ', '</th')
	soup = BeautifulSoup(response_text)
	mps = {}
	for mp in soup.find_all(u'sessionmaður'):
		try:
			mp_id = mp['id']
			short_name = mp.find(u'skammstöfun').contents[0]
			mps[mp] = {'short_name': }
			print mps[mp]
		except Exception as e:
			print 'failed', mp, e
	return mps

#get the data
data = get_mps(144)

print data

#write to json
with open('mps.js', 'w+') as outfile:
    json.dump(data, outfile)

#output csv file
with open(u'nefndarfundir.csv', 'w+') as csvfile:
    for mp_id in data:
    	line = mp_id + ',' + str(data[mp_id]) + '\n'
    	csvfile.write(line)