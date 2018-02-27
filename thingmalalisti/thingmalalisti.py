# -*- coding: utf-8 -*-

import requests
import xmltodict
from datetime import datetime

session = 148
url = "http://www.althingi.is/altext/xml/thingmalalisti/?lthing="

def get_mp_party(url, session):
	response = requests.get(url)
	data = xmltodict.parse(response.text)
	try:
		if data[u'þingmaður'][u'þingsetur'][u'þingseta'][u'þing'] == str(session):
			print(data[u'þingmaður'][u'þingsetur'][u'þingseta'][u'þingflokkur'][u'#text'])
			return data[u'þingmaður'][u'þingsetur'][u'þingseta'][u'þingflokkur'][u'#text']
	except Exception as e:
		for session_data in data[u'þingmaður'][u'þingsetur'][u'þingseta']:
			if session_data[u'þing'] == str(session):
				return session_data[u'þingflokkur'][u'#text']
	return None

def get_party_mps(session):
	url = "http://www.althingi.is/altext/xml/thingmenn/?lthing="
	response = requests.get(url+str(session))
	data = xmltodict.parse(response.text)
	results = {} #{flokkur1: [mp1, mp2], flokkur2: ...}
	for mp in data[u'þingmannalisti'][u'þingmaður']:
		mp_party = get_mp_party(mp[u'xml'][u'þingseta'], session)
		mp_name = mp[u'nafn']
		if mp_party in results:
			results[mp_party].append(mp_name)
		else:
			results[mp_party] = [mp_name]
	return results

def get_flutningsmenn_data(url):
	response = requests.get(url)
	data = xmltodict.parse(response.text)
	if u'nefnd' in data[u'þingskjal'][u'þingskjal'][u'flutningsmenn']:
		try:
			flutningsmenn = data[u'þingskjal'][u'þingskjal'][u'flutningsmenn'][u'nefnd'][u'flutningsmaður'][0][u'nafn']
		except:
			try:
				flutningsmenn = data[u'þingskjal'][u'þingskjal'][u'flutningsmenn'][u'nefnd'][u'flutningsmaður'][u'nafn']
			except:
				flutningsmenn = ''
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

print("Collecting party info")
parties = get_party_mps(session)

#import sys
#sys.exit()

query = url+str(session)
response = requests.get(query)
#print response.text.encode('utf-8', 'ignore')
data = xmltodict.parse(response.text)

f = open(str(session), 'w')
f.close()

party_issue_count = {"None": 0}
for k in parties.keys():
	party_issue_count[k] = 0

mp_issue_count = {}

def get_mp_party(mp, parties):
	#print(mp)
	for party in parties:
		if mp in parties[party]:
			return party
	return None

for issue in data[u'málaskrá'][u'mál']:
	if 'bmal' in issue[u'xml']:
		continue #óundirbúinn fyrirspurnartími, sleppa
	print('processing: ' + issue[u'@málsnúmer'])
	with open(str(session), 'a') as f:
		issue_data = get_issue_data(issue[u'xml'])
		issue_name = issue[u'málsheiti']
		issue_id = issue[u'@málsnúmer']
		issue_xml = issue[u'xml']
		issue_type = issue[u'málstegund'][u'@málstegund']
		party_issue_count[str(get_mp_party(str(issue_data['mps']), parties))] += 1
		try:
			mp_issue_count[str(issue_data['mps'])] += 1
		except:
			mp_issue_count[str(issue_data['mps'])] = 1
		issue_mps = str(issue_data['mps'])
		issue_status = issue_data['issue_status']
		f.write(issue_id + ';' + issue_name + ';' + issue_xml + ';' + issue_type + ';' + issue_mps + ';' + issue_status + '\n')
print(party_issue_count)
print(mp_issue_count)