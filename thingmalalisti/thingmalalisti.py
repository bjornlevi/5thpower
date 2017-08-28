# -*- coding: utf-8 -*-

import requests
import xmltodict
from datetime import datetime

sessions = list(range(146,147))
url = "http://www.althingi.is/altext/xml/thingmalalisti/?lthing="

def get_thingskjal(url):
	response = requests.get(url)
	data = xmltodict.parse(response.text)
	if u'nefnd' in data[u'þingskjal'][u'þingskjal'][u'flutningsmenn']:
		try:
			return data[u'þingskjal'][u'þingskjal'][u'flutningsmenn'][u'nefnd'][u'flutningsmaður'][0][u'nafn']
		except:
			return data[u'þingskjal'][u'þingskjal'][u'flutningsmenn'][u'nefnd'][u'flutningsmaður'][u'nafn']
	try:
		return data[u'þingskjal'][u'þingskjal'][u'flutningsmenn'][u'flutningsmaður'][0][u'nafn']
	except:
		return data[u'þingskjal'][u'þingskjal'][u'flutningsmenn'][u'flutningsmaður'][u'nafn']

def get_mal(url):
	response = requests.get(url)
	data = xmltodict.parse(response.text)
	thingskjal_url = ''
	try:

		try:
			thingskjal_url = data[u'þingmál'][u'þingskjöl'][u'þingskjal'][0][u'slóð'][u'xml']
		except:
			thingskjal_url = data[u'þingmál'][u'þingskjöl'][u'þingskjal'][u'slóð'][u'xml']
	except:
		return ''
	return get_thingskjal(thingskjal_url)

def get_flutningsmenn(url):
	return get_mal(url)

def get_names(url, malstegund):
	return get_flutningsmenn(url)
	#if malstegund == 'l':
	#	return get_flutningsmenn(url)
	#elif malstegund == 'f':
	#elif malstegund == 'm':
	#elif malstegund == 'n':
	#elif malstegund == 'b':
	#elif malstegund == 'q':
	#	return get_flutningsmenn(url)
	#elif malstegund == 'um':
	#elif malstegund == 'a':
	#	return get_flutningsmenn(url)
	#elif malstegund == 's':
	#elif malstegund == 'ft':

#málstegund: heiti
#málstegundir
#{('l', 'Frumvarp til laga'), 
#('f', 'Tillaga til þingsályktunar'), 
#('m', 'Fyrirspurn'), 
#('n', 'Álit'), 
#('b', 'Beiðni um skýrslu'), 
#('q', 'Fyrirspurn'), 
#('um', 'sérstök umræða'), 
#('a', 'Tillaga til þingsályktunar'), 
#('s', 'Skýrsla'), 
#('ft', 'óundirbúinn fyrirspurnatími')}
malstegund = {
	'l': 'Frumvarp til laga', 
	'f': 'Tillaga til þingsályktunar', 
	'm': 'Fyrirspurn',
	'n': 'Álit',
	'b': 'Beiðni um skýrslu',
	'q': 'Fyrirspurn',
	'um': 'sérstök umræða',
	'a': 'Tillaga til þingsályktunar',
	's': 'Skýrsla',
	'ft': 'óundirbúinn fyrirspurnatími'}

thingmal = {
	'l': {},
	'f': {},
	'm': {},
	'n': {},
	'b': {},
	'q': {},
	'um': {},
	'a': {},
	's': {},
	'ft': {}
}

query = url+str(146)
response = requests.get(query)
#print response.text.encode('utf-8', 'ignore')
data = xmltodict.parse(response.text)

f = open('146', 'w')
f.close()

for issue in data[u'málaskrá'][u'mál']:
	print('processing: ' + issue[u'xml'])
	with open('146', 'a') as f:
		f.write(str(get_names(issue[u'xml'], issue[u'málstegund'][u'@málstegund'])) + ';' + issue[u'málsheiti']+ ';' + issue[u'xml'] + ';' + issue[u'málstegund'][u'@málstegund']+'\n')