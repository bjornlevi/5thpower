# -*- coding: utf-8 -*-

import requests
import xmltodict
from bs4 import BeautifulSoup

#Ná í öll mál
def get_mal(session):
	url = 'https://www.althingi.is/altext/xml/thingmalalisti/?lthing=' +str(session)
	response = requests.get(url)
	data = xmltodict.parse(response.text)
	mal = []
	for m in data[u'málaskrá'][u'mál']:
		if(m[u'málstegund'][u'@málstegund']) in ['l', 'a']:
			mal.append(m[u'xml'])
	return mal

def get_size(doc):
	response = requests.get(doc)
	soup = BeautifulSoup(response.text, 'lxml')
	return len(soup.find("div", id="thingskjal"))

nefndaralit = []
for thing_nr in range(50, 150):
	print('processing ' + str(thing_nr))
	for mal_xml in get_mal(thing_nr):
		response = requests.get(mal_xml)
		data = xmltodict.parse(response.text)
		#finna nefndarálit
		try:
			for skjal in data[u'þingmál'][u'þingskjöl'][u'þingskjal']:
				if skjal[u'skjalategund'] == u'nefndarálit':
					size = get_size(skjal[u'slóð'][u'html'])
					print(size)
					nefndaralit.append([size, skjal[u'slóð'][u'html']])
		except:
			pass
print(max(nefndaralit))