# -*- coding: utf-8 -*-

import requests
import xmltodict
from datetime import datetime

def get_nefndir(session):
	url = 'http://www.althingi.is/altext/xml/nefndir/?lthing='+str(session)
	response = requests.get(url)
	data = xmltodict.parse(response.text)
	nefndir = []
	for i in data[u'nefndir']:
		for nefnd in data[u'nefndir'][i]:
			nefndir.append((nefnd[u'@id'], nefnd[u'heiti']))
	return nefndir

def get_mps(session):
	url = 'http://www.althingi.is/altext/xml/nefndir/nefndarmenn/?lthing='+str(session)
	response = requests.get(url)
	data = xmltodict.parse(response.text)
	mps = {}
	for i in data[u'nefndarmenn']:
		for nefnd in data[u'nefndarmenn'][i]:
			info_nefnd = {
				'id': nefnd[u'@id'],
				'heiti': nefnd[u'heiti'] 
			}
			for mp in nefnd[u'nefndarmaður']:
				if mp[u'nafn'] in mps:
					mps[mp[u'nafn']].append(info_nefnd)
				else:
					mps[mp[u'nafn']] = [info_nefnd]
	return mps

def get_fundir(session):
	url = 'http://www.althingi.is/altext/xml/nefndarfundir/?lthing='+str(session)
	response = requests.get(url)
	data = xmltodict.parse(response.text)
	attendance = []
	#counts = 0
	for fundur in data[u'nefndarfundir'][u'nefndarfundur']:
		try:
			fundargerd = requests.get(fundur[u'nánar'][u'fundargerð'][u'xml'])
			fundargerd_data = xmltodict.parse(fundargerd.text)
			maeting = fundargerd_data[u'nefndarfundur'][u'fundargerð'][u'texti'].split('</h2>')[1].split('<BR><BR>')[0]
			mps = maeting.split('<BR>')
			print(maeting)
			mps = [i.split(' (')[0] for i in mps]
			print(fundargerd_data[u'nefndarfundur'][u'@númer'])
			attendance.extend(mps)
			#if counts > 2:
				#break
			#else:
				#counts += 1
		except:
			pass
	return attendance


mp_nefndir = get_mps(146)
nefndir = get_nefndir(146)
#print(mp_nefndir.keys())
nefndarfundir = 'http://www.althingi.is/altext/xml/nefndarfundir/?lthing=146'
fundir = get_fundir(146)
#print(fundir)
for mp in mp_nefndir.keys():
	print(mp+';'+str(fundir.count(mp)))