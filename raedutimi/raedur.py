# -*- coding: utf-8 -*-

import requests
import xmltodict
from datetime import datetime
import re

session = 151
url = 'http://www.althingi.is/altext/xml/raedulisti/?lthing='

def calc_speech(start, end, speech):
	time1 = datetime.strptime(start, '%Y-%m-%dT%H:%M:%S')
	time2 = datetime.strptime(end, '%Y-%m-%dT%H:%M:%S')
	l = speech.split(' ')
	l.remove('') #remove empty strings where there can be extra spaces in text
	speech_lenght = (time2-time1).total_seconds()
	return [len(l) / (speech_lenght / 60), speech_lenght]


def get_speech(url):
	response = requests.get(url)
	data = xmltodict.parse(response.text)
	results = ''
	for mgr in data[u'ræða'][u'ræðutexti'][u'mgr']:
		try:
			results += mgr + ' '
		except:
			try:
				results += mgr['#text'] + ' '
			except:
				try:
					results += mgr[u'atburður']['#text'] + ' '
				except: 
					try:
						results += mgr[u'atburður'] + ' '
					except:
						try:
							results += ' '.join(mgr[u'vísa'][0][u'erindi'][0][u'lína']) + ' '
						except:
							try:
								results += mgr[u'forseti']['#text'] + ' '
							except:
								try:
									results += ' '.join(mgr[u'vísa'][u'erindi'][u'lína']) + ' '
								except:
									print(mgr)
	return results

speakers = {}

print("session", str(session))
try:
	query = url+str(session)
	response = requests.get(query)
	data = xmltodict.parse(response.text)
	for r in data[u'ræðulisti'][u'ræða']:
		try:
			s = r[u'ræðumaður'][u'forsetiAlþingis']
			print("ræðumaður er forseti þings, sleppa")
			continue
		except:
			pass
		speech = ''
		try:
			speech = get_speech(r[u'slóðir'][u'xml'])
			speech = re.sub(r'\(.+?\)', '', speech) #remove (.*) ex. https://www.althingi.is/altext/raeda/147/rad20170926T143427.html
			speaker = r[u'ræðumaður'][u'nafn']
			speech_start = r[u'ræðahófst']
			print(speaker + ':' + speech_start)
			speech_end = r[u'ræðulauk']
			speech_type = r[u'tegundræðu'] 
			# vista gögn
			speed = calc_speech(speech_start, speech_end, speech)
			if speed[1] > 90:
				if speed[0] > 250 or speed[0] < 50:
					pass
				elif u'Gjört á Bessastöðum' in speech: #skip these speeches
					pass
				else:
					try:
						speakers[speaker].append([speed[0], r[u'slóðir'][u'xml']])
					except:
						speakers[speaker] = [[speed[0], r[u'slóðir'][u'xml']]]
		except Exception as e:
			print(e)
except Exception as e:
	print(e)

print(speakers)

with open(u'ræðuhraði'+str(session)+'.txt', 'w') as f:
	f.write('þingmaður, orð á mín, hraðasta ræða, url, hægasta ræða, url\n')
	for speaker in speakers:
		l= speakers[speaker]
		s_l = [i[0] for i in l]
		mx = max(l)
		mn = min(l)
		print(speaker, s_l, mx[0], mx[1], mn[0], mn[1])
		f.write(speaker+','+str(int(sum(s_l)/len(s_l)))+','+str(int(mx[0]))+','+str(mx[1])+','+str(int(mn[0]))+','+str(mn[1])+'\n')