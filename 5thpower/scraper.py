#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import requests
from thingmadur import Thingmadur
from thingfundur import Thingfundur
import re

class Scraper:
	#page = requests.get('http://econpy.pythonanywhere.com/ex/001.html')
	url = 'http://www.althingi.is'

	def thing(self, type, thing):
		url = self.url + '/vefur/thingmalalisti.html?cmalteg='+type+'&validthing='+thing
		page = requests.get(url)
		page.encoding = 'utf-8'
		soup = BeautifulSoup(page.text)
		return str([o['value'].encode('ascii') for o in soup.find_all('option') if len(o['value'])>0])

	def fundur(self, url):
		if url.find("http://www.althingi.is/altext/")==-1:
			return {"error":"enginn fundur"}
		response = requests.get(url)
		soup = BeautifulSoup(response.text)
		return str(soup.find_all('efy'))

	def fundir(self, thing):
		response = requests.get('http://www.althingi.is/dba-bin/fulist.pl?ltg='+thing)
		soup = BeautifulSoup(response.text)
		thing_fundir = []
		for tr in soup.find_all('tr'):
			try:
				fundur_info = tr.find_all('td')
				if tr.td.a['href'].find('altext')>-1:
					print fundur_info
					print '---'
					nafn = tr.td.text
					dags = fundur_info[1].text + fundur_info[2].text + ')'
					url = self.url + tr.td.a['href']
					thing_fundir.append(Thingfundur(nafn, dags, url).to_json())
			except Exception as e:
				pass
		return thing_fundir[1:]

	def read_table_search_results(self, url):
		response = requests.get(url)
		soup = BeautifulSoup(response.text)
		return soup.find(id="t_thingmenn").find_all('tr')

	def thingmenn(self, thing):
		#response = requests.get('http://www.althingi.is/dba-bin/thmn.pl?thing='+thing)
		#soup = BeautifulSoup(response.text)
		soup = BeautifulSoup(open('tmp.html'))
		thingmannalisti = []
		for tr in soup.find(id="t_thingmenn").find_all('tr'):
			try:
				thingmadur_info = tr.find_all('td')
				url = "asdf"#self.url + thingmadur_info[1].a['href']
				nafn = "asdf"#thingmadur_info[1].a.text
				skammstofun = "skammstofun"#re.search('\(.*\)', str(thingmadur_info[1])).group()[1:-1]
				titill = "titill"
				kjordaemi = "kjordaemi"
				thingmannalisti.append(Thingmadur(nafn, skammstofun, titill, url, kjordaemi).to_json())
			except Exception as e:
				print e
		return str(thingmannalisti)

	def thingflokkar(self):
		response = requests.get('http://www.althingi.is/vefur/thingfl.html')
		soup = BeautifulSoup(response.text)
		parties = soup.find_all('li')

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
				try:
					member_info = row.find_all('td')
					nafn = row.td.a.text
					skammstofun = re.search('\(.*\)', str(row.td)).group()[1:-1]
					titill = member_info[1].span.text
					url = self.url + row.td.a['href']
					kjordaemi = member_info[2].span.text
					party_info[party_id]["members"].append(Thingmadur(nafn, skammstofun, titill, url, kjordaemi).to_json())
				except Exception as e:				
					pass #print e
		return party_info

	def collect_votes(self, current):
		results = []
		try:
			while current.nextSibling.name != 'h2':
				current = current.nextSibling
				if current.name == 'nobr':
					results.append(current.text)
		except:
			pass
		return results

	def is_vote(self, vote_id):
		response = requests.get('http://www.althingi.is/dba-bin/atkvgr.pl?nnafnak='+str(vote_id))
		soup = BeautifulSoup(response.text)
		nobrs = soup.find_all('nobr')
		if len(nobrs)==0:
			return False
		return True

	def get_all_votes(self):
		vote_results = {}
		for i in range(60000):
			print "running vote_id:" + str(i)
			if self.is_vote(i):
				vote_results[i] = self.atkvaedi(i)
		return vote_results

	def atkvaedi(self, vote_id):
		response = requests.get('http://www.althingi.is/dba-bin/atkvgr.pl?nnafnak='+str(vote_id))
		soup = BeautifulSoup(response.text)

		#<h2 class="FyrirsognSv">já:</h2>
		#<h2 class="FyrirsognSv">nei:</h2>
		#<h2 class="FyrirsognSv">greiðir ekki atkvæði:</h2>
		#<h2 class="FyrirsognSv">fjarvist:</h2>

		votes = {}
		for header in soup.find_all('h2'):
			if header.text == u'já:':
				#handle yes
				votes['yes'] = self.collect_votes(header)
			elif header.text == u'nei:':
				#handle no
				votes['no'] = self.collect_votes(header)
			elif header.text == u'greiðir ekki atkvæði:':
				#handle no vote
				votes['no_vote'] = self.collect_votes(header)
			elif header.text == u'fjarvist:':
				#handle absent
				votes['absent'] = self.collect_votes(header)
		return votes