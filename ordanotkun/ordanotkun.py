# -*- coding: utf-8 -*-

import requests
import xmltodict
import sqlite3

#create db and tables
conn = sqlite3.connect('ordanotkun.db')
c = conn.cursor()
try:
	#save speech/speaker/session/speech start/speech end
	c.execute('''CREATE TABLE ordanotkun(
		speech_text text, 
		speaker text, 
		session text, 
		speech_start text, 
		speech_end text,
		speech_type text
	)''')
except:
	#table exists
	pass


sessions = list(range(146,147))
url = 'http://www.althingi.is/altext/xml/raedulisti/?lthing='

def get_speech(url):
	response = requests.get(url)
	data = xmltodict.parse(response.text)
	results = ''
	for mgr in data[u'ræða'][u'ræðutexti'][u'mgr']:
		results += mgr + ' '
	return results

for session in sessions:
	print("session", str(session))
	query = url+str(session)
	response = requests.get(query)
	data = xmltodict.parse(response.text)
	for r in data[u'ræðulisti'][u'ræða']:
		try:
			speech = get_speech(r[u'slóðir'][u'xml'])
			speaker = r[u'ræðumaður'][u'nafn']
			speech_start = r[u'ræðahófst']
			speech_end = r[u'ræðulauk']
			speech_type = r[u'tegundræðu']
			# vista gögn
			values = (speech.lower(), speaker, session, speech_start, speech_end, speech_type)
			c.execute('insert into ordanotkun values(?,?,?,?,?,?)', values)
			conn.commit()
			print(str(session), "Speech saved", speaker)
		except:
			pass
	conn.close()