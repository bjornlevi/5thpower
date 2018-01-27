# -*- coding: utf-8 -*-

import requests
import xmltodict
from datetime import datetime

session = 148
url = "http://www.althingi.is/altext/xml/thingmalalisti/?lthing="

def get_flutningsmenn_data(url):
	response = requests.get(url)
	data = xmltodict.parse(response.text)
	if u'nefnd' in data[u'þingskjal'][u'þingskjal'][u'flutningsmenn']:
		try:
			flutningsmenn = data[u'þingskjal'][u'þingskjal'][u'flutningsmenn'][u'nefnd'][u'flutningsmaður'][0][u'nafn']
		except:
			flutningsmenn = data[u'þingskjal'][u'þingskjal'][u'flutningsmenn'][u'nefnd'][u'flutningsmaður'][u'nafn']
	try:
		flutningsmenn = data[u'þingskjal'][u'þingskjal'][u'flutningsmenn'][u'flutningsmaður'][0][u'nafn']
	except:
		try:
			flutningsmenn = data[u'þingskjal'][u'þingskjal'][u'flutningsmenn'][u'flutningsmaður'][u'nafn']
		except:
			flutningsmenn = ''
	return flutningsmenn

def get_issue_data(url):
	response = requests.get(url)
	data = xmltodict.parse(response.text)
	thingskjal_url = ''
	try:
		issue_status = data[u'þingmál'][u'mál'][u'staðamáls']
	except:
		issue_status = ''
	try:
		try:
			thingskjal_url = data[u'þingmál'][u'þingskjöl'][u'þingskjal'][0][u'slóð'][u'xml']
		except:
			thingskjal_url = data[u'þingmál'][u'þingskjöl'][u'þingskjal'][u'slóð'][u'xml']
	except:
		return ''
	return {'mps': get_flutningsmenn_data(thingskjal_url), 'issue_status': issue_status}

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

query = url+str(session)
response = requests.get(query)
#print response.text.encode('utf-8', 'ignore')
data = xmltodict.parse(response.text)

f = open(str(session), 'w')
f.close()

for issue in data[u'málaskrá'][u'mál']:
	if 'bmal' in issue[u'xml']:
		continue #óundirbúinn fyrirspurnartími, sleppa
	print('processing: ' + issue[u'xml'])
	with open(str(session), 'a') as f:
		issue_data = get_issue_data(issue[u'xml'])
		issue_name = issue[u'málsheiti']
		issue_xml = issue[u'xml']
		issue_type = issue[u'málstegund'][u'@málstegund']
		issue_mps = str(issue_data['mps'])
		issue_status = issue_data['issue_status']
		f.write(issue_name + ';' + issue_xml + ';' + issue_type + ';' + issue_mps + ';' + issue_status + '\n')