# -*- coding: utf-8 -*-

import requests
import xmltodict
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from private_data import sheet_key
import sys

#initialize 
session = None
try:
	session = sys.argv[1]
except:
	sys.exit(0)
url = "http://www.althingi.is/altext/xml/thingmalalisti/?lthing="

# use creds to create a client to interact with the Google Drive API
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
client = gspread.authorize(creds)

#create new worksheet to store the data
doc = client.open_by_key(sheet_key)
try:
	doc.add_worksheet(str(session), 0, 0)
	data_sheet = doc.worksheets()[-1]
except:
	data_sheet= doc.worksheet(str(session))

# Extract and print all of the values
#list_of_hashes = sheet.get_all_records()
#import sys
#sys.exit()

#functions
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
		try:
			mp_party = get_mp_party(mp[u'xml'][u'þingseta'], session)
		except:
			mp_party = None
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
			flutningsmenn = data[u'þingskjal'][u'þingskjal'][u'flutningsmenn'][u'nefnd'][u'heiti']
		except:
			flutningsmenn = ''
		return flutningsmenn

	try:
		if u'ráðherra' in data[u'þingskjal'][u'þingskjal'][u'flutningsmenn'][u'flutningsmaður'][0]:
			flutningsmenn = data[u'þingskjal'][u'þingskjal'][u'flutningsmenn'][u'flutningsmaður'][0][u'ráðherra']
		else:
			flutningsmenn = data[u'þingskjal'][u'þingskjal'][u'flutningsmenn'][u'flutningsmaður'][0][u'nafn']
	except:
		try:
			if u'ráðherra' in data[u'þingskjal'][u'þingskjal'][u'flutningsmenn'][u'flutningsmaður']:
				flutningsmenn = data[u'þingskjal'][u'þingskjal'][u'flutningsmenn'][u'flutningsmaður'][u'ráðherra']
			else:
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
	try:
		if data[u'þingmál'][u'ræður'][u'ræða'][0][u'tegundræðu'] == 'flutningsræða' or data[u'þingmál'][u'ræður'][u'ræða'][1][u'tegundræðu'] == 'flutningsræða':
			issue_introduction = data[u'þingmál'][u'ræður'][u'ræða'][0][u'ræðahófst']
		else:
			issue_introduction = ''
	except Exception as e:
		issue_introduction = ''
	return {'mps': get_flutningsmenn_data(thingskjal_url), 'issue_status': issue_status, 'issue_introduction': issue_introduction}

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

google_data = []
for issue in data[u'málaskrá'][u'mál']:
	if 'bmal' in issue[u'xml']:
		continue #óundirbúinn fyrirspurnartími, sleppa
	print('processing: ' + issue[u'@málsnúmer'])
	with open(str(session), 'a') as f:
		issue_data = get_issue_data(issue[u'xml'])
		issue_name = issue[u'málsheiti']
		issue_id = issue[u'@málsnúmer']
		issue_xml = issue[u'xml']
		issue_html = issue[u'html']
		issue_type = issue[u'málstegund'][u'@málstegund']
		issue_party = str(get_mp_party(str(issue_data['mps']), parties))
		party_issue_count[str(get_mp_party(str(issue_data['mps']), parties))] += 1
		try:
			mp_issue_count[str(issue_data['mps'])] += 1
		except:
			mp_issue_count[str(issue_data['mps'])] = 1
		issue_mps = str(issue_data['mps'])
		issue_status = issue_data['issue_status']
		issue_introduction = issue_data['issue_introduction']
		google_data.append([issue_id, issue_name, issue_html, issue_type, issue_mps, issue_party, issue_status, issue_introduction])

# Cell range
cell_list = data_sheet.range(1,1,len(google_data),len(google_data[0]))

# Update cells
cell_nr = 0
for issue in google_data:
	for val in issue:
		cell_list[cell_nr].value=val
		cell_nr += 1
#for cell in cell_list:
#   	cell.value = 'O_o'

# Update in batch
data_sheet.update_cells(cell_list)

print(party_issue_count)
print(mp_issue_count)
print()