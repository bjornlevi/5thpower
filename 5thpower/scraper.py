#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import requests
from thingmadur import Thingmadur
import re

class Scraper:
	#page = requests.get('http://econpy.pythonanywhere.com/ex/001.html')
	url = 'http://www.althingi.is'

	def thing(self, type, thing):
		url = self.url + '/vefur/thingmalalisti.html?cmalteg='+type+'&validthing='+thing
		page = requests.get(url)
		page.encoding = 'utf-8'
		soup = BeautifulSoup(page.text)
		return str(soup.find_all('option'))


	def read_table_search_results(self, url):
		response = requests.get(url)
		soup = BeautifulSoup(response.text)
		return soup.find(id="t_thingmenn").find_all('tr')

	def thingflokkar(self):
		response = requests.get('http://www.althingi.is/vefur/thingfl.html')
		soup = BeautifulSoup(response.text)
		parties = soup.find_all('li')
		query_path = "http://www.althingi.is"

		party_info = {}

		for li in parties[0::3]:
			party_id = li.a['href'][1:]
			party_info[party_id] = {'name': li.a.text}
			party_structure = li.ul.find_all('li')
			party_gov = party_structure[0]
			party_members = party_structure[1]
			gov_members = self.read_table_search_results(query_path + party_gov.a['href'])
			member_list = self.read_table_search_results(query_path + party_members.a['href'])
			party_info[party_id]["gov"] = {}
			for row in gov_members:
				try:
					if row.td.text.find(u'varaformaður') == -1:
						party_info[party_id]["gov"]['chair'] = row.td.a.text
					else:
						party_info[party_id]["gov"]['deputy_chair'] = row.td.a.text
					#print party_info[party_id]
				except Exception as e:				
					pass #print e

			party_info[party_id]["members"] = []
			for row in member_list:
				print row
				print '---'
				try:
					member_info = row.find_all('td')
					nafn = row.td.a.text
					skammstofun = re.search('\(.*\)', str(row.td)).group()[1:-1]
					titill = member_info[1].span.text
					url = query_path + row.td.a['href']
					kjordaemi = member_info[2].span.text
					party_info[party_id]["members"].append(Thingmadur(nafn, skammstofun, titill, url, kjordaemi).to_json())
				except Exception as e:				
					print e
		return party_info		