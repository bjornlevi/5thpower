# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import re

def get_fjarvistir(url):
	response = requests.get(url)
	soup = BeautifulSoup(response.text)
	results = []
	for fjarvist in soup('p'):
		results.append(fjarvist.text)
	return results

def find_fjarvistir(url):
	response = requests.get(url)
	soup = BeautifulSoup(response.text)
	is_fjarvist = soup.find(text="Fjarvistarleyfi")
	if is_fjarvist:
		return get_fjarvistir(is_fjarvist.parent.parent['href'])

def collect_fjarvistir():
	response = requests.get('http://www.althingi.is/vefur/altutg.html')
	soup = BeautifulSoup(response.text)
	things = soup.find_all(href=re.compile('/dba-bin/fulist.pl'))
	query_path = "http://www.althingi.is"

	by_thing = {}

	for thing in things[1:]:
		print thing.text
		by_thing[thing.text] = {}
		response = requests.get(query_path + thing['href'])
		soup = BeautifulSoup(response.text)
		fundir = soup.find_all(href=re.compile('/altext/'))
		for fundur in fundir:
			print fundur
			try:
				by_thing[thing.text][fundur.text] = find_fjarvistir(query_path + fundur['href'])
			except:
				pass
			#print fundur_name, fundur_link
		f = open(thing.text, 'w')
		f.write(str(by_thing[thing.text]))
		by_thing = {}
		
collect_fjarvistir()