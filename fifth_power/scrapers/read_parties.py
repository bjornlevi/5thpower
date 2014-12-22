#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient, Connection

from utility import get_party_info, get_party_description

connection_name = "althingi"
party_collection = "parties"
connection = Connection()
db = connection[connection_name]

def collect_parties():
	response = requests.get('http://www.althingi.is/vefur/thingfl.html')
	soup = BeautifulSoup(response.text)
	party_info = get_party_description()
	return party_info