# -*- coding: utf-8 -*-

import requests
import xmltodict

sessions = list(range(137,142))
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

	with open(u'atkvæðatalning'+str(session)+'.txt', 'w') as f:
		f.write('þingmaður, já, nei, sat hjá, boðaði fjarvist, fjarverandi\n')
		for mp in mp_votes:
			f.write(mp +','+ str(mp_votes[mp].count('já')) +','+ str(mp_votes[mp].count('nei')) +','+ str(mp_votes[mp].count('greiðir ekki atkvæði')) +','+ str(mp_votes[mp].count('boðaði fjarvist')) +','+ str(mp_votes[mp].count('fjarverandi'))+'\n')
