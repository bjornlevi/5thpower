#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import requests

class Scraper:
	#page = requests.get('http://econpy.pythonanywhere.com/ex/001.html')
	url = 'http://www.althingi.is'

	def thing(self, type, thing):
		url = self.url + '/vefur/thingmalalisti.html?cmalteg='+type+'&validthing='+thing
		page = requests.get(url)
		page.encoding = 'utf-8'
		soup = BeautifulSoup(page.text)
		return str(soup.find_all('option'))