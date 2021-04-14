# -*- coding: utf-8 -*-

import requests
import xmltodict
from datetime import datetime, timedelta
from fuzzywuzzy import process
import sys
from os import path

session = None
try:
	session = sys.argv[1]
except:
	sys.exit(0)

def strip_url(url):
	return url.replace('/', '-').replace(':','-').replace('?','-').replace('=','-')

def get_url_or_saved(url):
	if path.exists("data/"+strip_url(url)):
		#print("opening saved document " + url)
		try:
			with open('data/'+strip_url(url), 'w') as f:
				return f.read()
		except: #corrupted document, get it again
			response = requests.get(url) #get data
			with open('data/'+strip_url(url), 'w') as f:
				f.write(response.text) #save data
			return response.text
	else:
		#print("opening document from url " + url)
		response = requests.get(url) #get data
		with open('data/'+strip_url(url), 'w') as f:
			f.write(response.text) #save data
		return response.text #continue

def get_nefndir(session):
	url = 'http://www.althingi.is/altext/xml/nefndir/?lthing='+str(session)
	response = get_url_or_saved(url)
	data = xmltodict.parse(response)
	nefndir = []
	for i in data[u'nefndir']:
		for nefnd in data[u'nefndir'][i]:
			nefndir.append((nefnd[u'@id'], nefnd[u'heiti']))
	return nefndir

def get_mps(session):
	url = 'http://www.althingi.is/altext/xml/nefndir/nefndarmenn/?lthing='+str(session)
	response = get_url_or_saved(url)
	data = xmltodict.parse(response)
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
	response = get_url_or_saved(url)
	data = xmltodict.parse(response)
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
					nefndasetu_lauk = ''
					try:
						nefndasetu_lauk = mp[u'nefndasetulauk']
					except:
						nefndasetu_lauk = datetime.strftime(datetime.now(), '%Y-%m-%d')
					if mp[u'nafn'] in mps:
						mps[mp[u'nafn']].append({
							'nefnd_id': info_nefnd['id'],
							'start': mp[u'nefndasetahófst'],
							'end': nefndasetu_lauk
						})
					else:
						mps[mp[u'nafn']] = [{
							'nefnd_id': info_nefnd['id'],
							'start': mp[u'nefndasetahófst'],
							'end': nefndasetu_lauk
						}]

				else:
					pass #nefndarmaður er áheyrnarfulltrúi eða varamaður
	return mps	

def get_fundir(session, mps_in_nefndir):
	url = 'http://www.althingi.is/altext/xml/nefndarfundir/?lthing='+str(session)
	response = get_url_or_saved(url)
	data = xmltodict.parse(response)
	fundir = []
	fundir_time = []
	for fundur in data[u'nefndarfundir'][u'nefndarfundur']:
		try:
			dagsetning = fundur[u'hefst'][u'dagur']
			nefnd_id = fundur[u'nefnd'][u'@id']
			fundargerd = get_url_or_saved(fundur[u'nánar'][u'fundargerð'][u'xml'])
			fundargerd_data = xmltodict.parse(fundargerd)
			fundur_settur = fundargerd_data[u'nefndarfundur'][u'fundursettur']
			fundur_slit = fundargerd_data[u'nefndarfundur'][u'fuslit']
			maeting = fundargerd_data[u'nefndarfundur'][u'fundargerð'][u'texti'].split('</h2>')[1].split('<BR><BR>')[0]
			#dæmi um maeting: Jón Gunnarsson (JónG) formaður, kl. 09:00 <BR>Ari Trausti Guðmundsson (ATG) 1. varaformaður, kl. 09:00 <BR>Líneik Anna Sævarsdóttir (LínS) 2. varaformaður, kl. 09:00 <BR>Bergþór Ólason (BergÓ), kl. 09:00 <BR>Björn Leví Gunnarsson (BLG), kl. 09:00 <BR>Guðjón S. Brjánsson (GBr), kl. 09:00 <BR>Hanna Katrín Friðriksson (HKF), kl. 09:00 <BR>Karl Gauti Hjaltason (KGH), kl. 09:00 <BR>Kolbeinn Óttarsson Proppé (KÓP), kl. 09:00 <BR>Vilhjálmur Árnason (VilÁ), kl. 09:00 
			#Willum Þór Þórsson (WÞÞ) formaður, kl. 09:00 <BR>Haraldur Benediktsson (HarB) 1. varaformaður, kl. 09:00 <BR>Ágúst Ólafur Ágústsson (ÁÓÁ), kl. 09:00 <BR>Birgir Þórarinsson (BirgÞ), kl. 09:00 <BR>Bjarkey Olsen Gunnarsdóttir (BjG) fyrir Steinunni Þóru Árnadóttur (SÞÁ), kl. 09:00 <BR>Björn Leví Gunnarsson (BLG), kl. 09:00 <BR>Njáll Trausti Friðbertsson (NTF), kl. 09:00 <BR>Þorsteinn Víglundsson (ÞorstV), kl. 09:00 
			attendance = maeting.split('<BR>')
			#Ari Trausti Guðmundsson (ATG) 1. varaformaður, kl. 09:00 
			#Bjarkey Olsen Gunnarsdóttir (BjG) fyrir Steinunni Þóru Árnadóttur (SÞÁ), kl. 09:00 
			mps = []
			mps_time_attendance = []
			for a in attendance:
				if 'fyrir' in a: #ef varamaður
					m = a.split('fyrir ')[1].split(' (')[0]
					#skrá mætingu varamanns á aðalmann
					mps.append(process.extractOne(m, mps_in_nefndir)[0]) 
					mps_time_attendance.append([process.extractOne(m, mps_in_nefndir)[0], a.split('kl. ')[1].strip()])
				else:
					#skrá mætingu aðalmanns
					mps.append(a.split(' (')[0])
					mps_time_attendance.append([a.split(' (')[0], a.split('kl. ')[1].strip()])
			#mps = [i.split(' (')[0] for i in attendance]
			fundir.append({'nefnd': nefnd_id, 'mps': mps, 'dagsetning': dagsetning})
			fundir_time.append({'nefnd': nefnd_id, 'mps': mps_time_attendance, 'dagsetning': dagsetning, 'fundur_settur': fundur_settur, 'fundur_slit': fundur_slit})
		except Exception as e:
			print(fundur[u'nefnd']['#text'] + ' - ' +  fundur[u'hefst'][u'texti'])
			print(e)
	return fundir, fundir_time

def count_nefndarfundir(session):
	url = 'http://www.althingi.is/altext/xml/nefndarfundir/?lthing='+str(session)
	response = get_url_or_saved(url)
	data = xmltodict.parse(response)
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

def get_mp_ids(session):
	url = 'http://www.althingi.is/altext/xml/thingmenn/?lthing='+str(session)
	response = get_url_or_saved(url)
	data = xmltodict.parse(response)
	mp_ids = {}
	for mp in data[u'þingmannalisti'][u'þingmaður']:
		mp_ids[mp[u'nafn']]=mp[u'@id']
	return mp_ids

mp_ids = get_mp_ids(session)
#{'Nafn': 'mp_id', ...}

def get_assembly_attendance(mps):
	mp_in_session = {}
	for mp in mps:
		mp_in_session[mp] = []
		url = 'http://www.althingi.is/altext/xml/thingmenn/thingmadur/thingseta/?nr='+mps[mp]
		response = get_url_or_saved(url)
		data = xmltodict.parse(response)
		for sitting in data[u'þingmaður'][u'þingsetur'][u'þingseta']:
			try:
				if sitting[u'tegund'] == 'þingmaður':
					if sitting[u'tímabil'][u'út'] == None:
						sitting[u'tímabil'][u'út'] = datetime.strptime(datetime.now(),'%d.%m.%Y')
					mp_in_session[mp].append([sitting[u'tímabil'][u'inn'], sitting[u'tímabil'][u'út']])
			except:
				#print(sitting, mp)
				pass
	return mp_in_session

def mp_in_attendance(mp, mp_in_session_dates, meeting_date):
	for sitting in mp_in_session_dates[mp]:
		if datetime.strptime(meeting_date, '%Y-%m-%d') >= datetime.strptime(sitting[0], '%d.%m.%Y') and datetime.strptime(meeting_date, '%Y-%m-%d') <= datetime.strptime(sitting[1], '%d.%m.%Y'):
			return True
	return False	

mp_nefndir = get_mps_adalnefndir(session)
#print(mp_nefndir)
#{'mp':[{'start':date, 'end':date, nefnd_id:id}, ...]
#{Guðjón S. Brjánsson: [{'end': '2017-01-24', 'nefnd_id': '201', 'start': '2016-12-19'}, ...], ...}
#for mp in mp_nefndir:
	#print(mp+';'+str(mp_nefndir[mp]))

mp_fundir, mp_fundir_time = get_fundir(session, mp_nefndir.keys())
#mp_fundir
#{
	#'mps': ['Haraldur Benediktsson', 'Oddný G. Harðardóttir', ...], 
	#'nefnd': '207', 
	#'dagsetning': '2016-12-07',
	#'fundur_settur': '2019-09-18T09:00:00',
	#'fundur_slit': '2019-09-18T12:09:00'
#}

#for fundur in mp_fundir:
	#print(fundur)

#mp_fundir_time
#{'mps': [['Haraldur Benediktsson', '09:00'], ['Oddný G. Harðardóttir', '09:00'], ...], 
#print(mp_fundir_time)

mp_attendance = get_assembly_attendance(mp_ids)
#{'Haraldur Benediktsson': [[date_inn, date_út], [date_inn, ...], ...], 'Oddný ...': [[...], ...]}

fjoldi_nefndarfunda = count_nefndarfundir(session)
#{'nefnd_id': fjöldi funda}
#{'201': 52, '203': ...}
#for nefnd in fjoldi_nefndarfunda:
	#print(nefnd+';'+str(fjoldi_nefndarfunda[nefnd]))

#nefndir = get_nefndir(146)
#print(mp_nefndir.keys())

with open(u'nefndir'+str(session)+'.txt', 'w') as f:
	f.write('þingmaður,Vænt mæting,Fjöldi mætinga,Seint\n')

	for mp in mp_nefndir.keys(): #skoðum hvern þingmann fyrir sig
		print(mp)
		total_meeting = 0 #heildarfjöldi funda sem mætt er á sem aðalmaður eða ekki.
		expected_meetings = 0 #fjöldi funda sem aðalmaður
		missed_meeting = 0 #mætti ekki sem aðalmaður
		backup_attends = 0 #varamaður er á þingi
		late = timedelta(minutes=0)
		for fundur in mp_fundir_time:

			if mp_in_nefnd(mp, fundur['nefnd'], mp_nefndir, fundur['dagsetning']) and mp_in_attendance(mp, mp_attendance, fundur['dagsetning']):
				expected_meetings += 1 #þingmaður er í nefnd, skráður á þing og ætti að mæta á fund		

			if mp in [i[0] for i in fundur['mps']]: #athuga hvort þingmaður er á mætingarlista
				total_meeting += 1 #þingmaður er á mætingarlista, skrá mætingu.


			#stundvísi = fundur_settur - mp[1]
			#print(fundur['fundur_settur'])
			for m in fundur['mps']:
				if m[0] == mp:
					#fundur['fundur_settur'] = datetime.strptime('2020-01-16T13:30:00', '%Y-%m-%dT%H:%M:%S')
					settur = datetime.strptime(fundur['fundur_settur'].split('T')[1], '%H:%M:%S')
					slit = datetime.strptime(fundur['fundur_slit'].split('T')[1], '%H:%M:%S')
					maettur = datetime.strptime(m[1], '%H:%M')
					d = maettur - settur
					if d > timedelta(minutes=0):
						#print(fundur['dagsetning'] + ': ' + str(d))
						#f.write(';;;;'+fundur['dagsetning']+' '+str(d)+'\n')
						late += d
			
		#print(mp+';'+str(total_meeting)+';'+str(expected_meetings)+';'+str(missed_meeting))
		f.write(mp+','+str(expected_meetings)+','+str(total_meeting)+','+str(late)+'\n')