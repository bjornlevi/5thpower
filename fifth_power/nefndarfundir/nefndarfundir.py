# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import json, re

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
	for nefndarfundur in soup.find_all(u'nefndarfundur'):
		try: 
			fundar_id = nefndarfundur[u'númer']

			dagskra = nefndarfundur.find(u'dagskrá')
			nefndarfundir[fundar_id] = {'dagskra': nefndarfundur.find('xml').contents[0]}

			nefnd = nefndarfundur.find('nefnd')
			nefndarfundir[fundar_id]['nefnd'] = {'id': nefnd['id'], 'nafn': nefnd.contents[0]}

			nefndarfundir[fundar_id]['dagur'] = nefndarfundur.find('dagur').contents[0]
			nefndarfundir[fundar_id]['timi'] = nefndarfundur.find('timi').contents[0]

			fundargerd = nefndarfundur.find(u'fundargerð')
			nefndarfundir[fundar_id]['fundargerd'] = fundargerd.find('xml').contents[0]

			nefndarfundir[fundar_id]['fundargerd_texti'] = get_fundargerd(nefndarfundir[fundar_id]['fundargerd'])
			nefndarfundir[fundar_id]['fundargerd_texti'] = nefndarfundir[fundar_id]['fundargerd_texti'].split("Nefndarritar")[0].split("<BR>")[4:]
		except Exception as e:
			failed.append(fundar_id)
	print failed
	return nefndarfundir

#get_fundargerdir_faerslunr(144)

with open('nefndarfundir.js', 'w+') as outfile:
    json.dump(get_fundargerdir_faerslunr(144), outfile)
