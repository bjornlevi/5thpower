# -*- coding: utf-8 -*-

import requests
import xmltodict

sessions = list(range(143,147))
url = 'http://www.althingi.is/altext/xml/atkvaedagreidslur/?lthing='

session_votes = {}
for session in sessions:
	print(session)
	query = url+str(session)
	response = requests.get(query)
	#print response.text.encode('utf-8', 'ignore')
	data = xmltodict.parse(response.text)

	mp_votes = {}
	for vote in data[u'atkvæðagreiðslur'][u'atkvæðagreiðsla']:
		vote_nr = vote[u'@atkvæðagreiðslunúmer']
		vote_query = 'http://www.althingi.is/altext/xml/atkvaedagreidslur/atkvaedagreidsla/?numer='+vote_nr
		vote_response = requests.get(vote_query)
		vote_data = xmltodict.parse(vote_response.text)
		try:
			for mp_vote in vote_data[u'atkvæðagreiðsla'][u'atkvæðaskrá'][u'þingmaður']:
				#print(vote_nr, mp_vote[u'nafn'], mp_vote[u'atkvæði'])
				if mp_vote[u'nafn'] in mp_votes:
					mp_votes[mp_vote[u'nafn']].append(mp_vote[u'atkvæði'])
				else:
					mp_votes[mp_vote[u'nafn']] = [mp_vote[u'atkvæði']]
		except:
			#print(vote_nr, 'engin atkvæðagreiðsla')
			pass #enginn hreyfir andmælum
	session_votes[session] = mp_votes

print('þingmaður, já, nei, sat hjá, boðaði fjarvist, fjarverandi')
for session in session_votes:
	print(session)
	for mp in session_votes[session]:
		print(mp +','+ str(session_votes[session][mp].count('já')) +','+ str(session_votes[session][mp].count('nei')) +','+ str(session_votes[session][mp].count('greiðir ekki atkvæði')) +','+ str(session_votes[session][mp].count('boðaði fjarvist')) +','+ str(session_votes[session][mp].count('fjarverandi')))