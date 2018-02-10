# -*- coding: utf-8 -*-

import requests
import xmltodict
from datetime import datetime

url = 'http://www.althingi.is/altext/xml/thingfundir/?lthing='
sessions = range(135,149)

for session in sessions:
	print(session)