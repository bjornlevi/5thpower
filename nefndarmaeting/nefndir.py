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
					mps[mp[u'nafn']].add(info_nefnd['id'])
				else:
					mps[mp[u'nafn']] = set(info_nefnd['id'])
	return mps

def get_mps_adalnefndir(session):
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
				#print(mp[u'nafn'], mp[u'staða'], info_nefnd['id'])
				if mp[u'staða'] in [u'nefndarmaður', u'formaður', u'1. varaformaður', u'2. varaformaður']:
					if mp[u'nafn'] in mps:
						mps[mp[u'nafn']].append({
							'nefnd_id': info_nefnd['id'],
							'start': mp[u'nefndasetahófst'],
							'end': mp[u'nefndasetulauk']
						})
					else:
						mps[mp[u'nafn']] = [{
							'nefnd_id': info_nefnd['id'],
							'start': mp[u'nefndasetahófst'],
							'end': mp[u'nefndasetulauk']
						}]

				else:
					pass #nefndarmaður er áheyrnarfulltrúi eða varamaður
	return mps	

def get_fundir(session):
	url = 'http://www.althingi.is/altext/xml/nefndarfundir/?lthing='+str(session)
	response = requests.get(url)
	data = xmltodict.parse(response.text)
	fundir = []
	for fundur in data[u'nefndarfundir'][u'nefndarfundur']:
		try:
			dagsetning = fundur[u'hefst'][u'dagur']
			nefnd_id = fundur[u'nefnd'][u'@id']
			fundargerd = requests.get(fundur[u'nánar'][u'fundargerð'][u'xml'])
			fundargerd_data = xmltodict.parse(fundargerd.text)
			maeting = fundargerd_data[u'nefndarfundur'][u'fundargerð'][u'texti'].split('</h2>')[1].split('<BR><BR>')[0]
			mps = maeting.split('<BR>')
			mps = [i.split(' (')[0] for i in mps]
			fundir.append({'nefnd': nefnd_id, 'mps': mps, 'dagsetning': dagsetning})
		except:
			pass
	return fundir

def count_nefndarfundir(session):
	url = 'http://www.althingi.is/altext/xml/nefndarfundir/?lthing='+str(session)
	response = requests.get(url)
	data = xmltodict.parse(response.text)
	nefndir = {}
	for fundur in data[u'nefndarfundir'][u'nefndarfundur']:
		#print(fundur[u'nefnd'])
		if fundur[u'nefnd'][u'@id'] in nefndir:
			nefndir[fundur[u'nefnd'][u'@id']] += 1
		else:
			nefndir[fundur[u'nefnd'][u'@id']] = 1
	return nefndir

def sum_mp_nefndarfundir(nefndir, nefndarfundir):
	"""
	mp = 'Nafn þingmanns'
	nefndir = {'nefnd_id1', 'nefnd_id2', ...}
	nefndarfundir = { 'nefnd_id1':fjöldi funda, 'nefnd_id2':fjöldi funda }
	"""
	fjoldi_funda = 0
	for nefnd in nefndir:
		try:
			fjoldi_funda += nefndarfundir[nefnd]
		except:
			pass #engir nefndarfundir í þessari nefnd
	return fjoldi_funda

def mp_in_nefnd(mp, nefnd, mp_nefndir, meeting_date):
	nefndir = mp_nefndir[mp]
	for n in nefndir:
		if n['nefnd_id'] == nefnd:
			if datetime.strptime(meeting_date, '%Y-%m-%d') >= datetime.strptime(n['start'], '%Y-%m-%d') and datetime.strptime(meeting_date, '%Y-%m-%d') <= datetime.strptime(n['end'], '%Y-%m-%d'):
				return True
	return False

session = 146

mp_nefndir = get_mps_adalnefndir(session)
#{'mp':[{'start':date, 'end':date, nefnd_id:id}, ...]
#{Guðjón S. Brjánsson: [{'end': '2017-01-24', 'nefnd_id': '201', 'start': '2016-12-19'}, ...], ...}
for mp in mp_nefndir:
	print(mp+';'+str(mp_nefndir[mp]))

fjoldi_nefndarfunda = count_nefndarfundir(session)
#{'nefnd_id': fjöldi funda}
#{'201': 52, '203': ...}
for nefnd in fjoldi_nefndarfunda:
	print(nefnd+';'+str(fjoldi_nefndarfunda[nefnd]))

#nefndir = get_nefndir(146)
#print(mp_nefndir.keys())

mp_fundir = get_fundir(session)
#{'mps': ['Haraldur Benediktsson', 'Oddný G. Harðardóttir', ...], 
#'nefnd': '207', 
#'dagsetning': '2016-12-07'}
#for fundur in mp_fundir:
	#print(fundur)

for mp in mp_nefndir.keys():
	total_meeting = 0
	expected_meetings = 0
	missed_meeting = 0
	for fundur in mp_fundir:
		if mp_in_nefnd(mp, fundur['nefnd'], mp_nefndir, fundur['dagsetning']):
			expected_meetings += 1 #fjöldi funda sem mp ætti að mæta á
			if mp in fundur['mps']:
				total_meeting += 1 #mættur og á að vera
			else:
				missed_meeting += 1 #ekki mættur en á að vera
				print(fundur['dagsetning'], fundur['nefnd'])
		else:
			if mp in fundur['mps']:
				total_meeting += 1 #mættur en á ekki að vera

	print(mp+';'+str(total_meeting)+';'+str(expected_meetings)+';'+str(missed_meeting))
