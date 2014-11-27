# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import re
from thingmadur import Thingmadur
#print response.text.encode('utf-8')

def read_table_search_results(url):
	response = requests.get(url)
	soup = BeautifulSoup(response.text)
	return soup.find(id="t_thingmenn").find_all('tr')

def collect_thingmenn():
	"""
		Read the althing.is vefur and returns a dictionary of all parliamentarians by their short by_short_names
		{
			'short_name': {
				'nafn': 'Someone Someson',
				'skammstofun': 'SS',
				'url': 'althingi.is/url/to/parliamentarian',
				'party': ['list', 'of', 'parties'],
				'thing': ['list', 'of', 'thing', 'sessions']
			},
			...

		}
	"""
	response = requests.get('http://www.althingi.is/vefur/thingfl.html')
	soup = BeautifulSoup(response.text)
	parties = soup.find_all('li')
	query_path = "http://www.althingi.is"

	by_short_names = {}

	for li in parties[0::3]:
		party_id = li.a['href'][1:]
		party_structure = li.ul.find_all('li')
		party_members = party_structure[1]
		member_list = read_table_search_results(query_path + party_members.a['href'])

		#current members of parliament
		for row in member_list:
			try:
				nafn = row.td.a.text
				skammstofun = re.search('\(.*\)', str(row.td)).group()[1:-1]
				#print row.find_all('td')[1].span.text
				url = query_path + row.td.a['href']
				t = Thingmadur(nafn, skammstofun, url)
				t.add_party(party_id)
				t.add_thing("144")
				by_short_names[skammstofun] = t
				print 'adding: ' + t.skammstofun
				#print t.to_json()
			except Exception as e:				
				pass

	#past members of parliament
	#http://www.althingi.is/dba-bin/thmn.pl
	past_parties = soup.find_all(href=re.compile("http://www.althingi.is/dba-bin/thmn.pl"))
	for pp in past_parties:
		try:
			party_id = pp.text
			print party_id
			member_list = read_table_search_results(pp['href'])
			for row in member_list:
				try:
					cols = row.find_all('td')
					thing = row.td.text
					nafn = cols[1].a.text
					skammstofun = re.search('\(.*\)', str(cols[1])).group()[1:-1]
					url = query_path + cols[1].a['href']
					if skammstofun in by_short_names:
						#þingmaður already added, add thing and possibly a new party
						print 'existing þingmaður: ' + skammstofun
						if party_id not in by_short_names[skammstofun].party:
							print 'adding party_id: ' + party_id
							by_short_names[skammstofun].add_party(party_id)
						print 'adding thing: ' + thing
						by_short_names[skammstofun].add_thing(thing)
						#print by_short_names[skammstofun].to_json()
						continue
					
					t = Thingmadur(nafn, skammstofun, url)
					t.add_party(party_id)
					t.add_thing(thing)
					by_short_names[skammstofun] = t
					#print t.to_json()
				except Exception as e:			
					print e
		except:
			pass

	return by_short_names

for thingmadur in collect_thingmenn():
	print thingmadur