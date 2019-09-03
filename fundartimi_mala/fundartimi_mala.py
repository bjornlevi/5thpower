# -*- coding: utf-8 -*-

import requests
import xmltodict
import re
from datetime import datetime, timedelta
from fuzzywuzzy import process
import sys

#Ná í öll mál
def get_mal(session):
	url = 'http://www.althingi.is/altext/xml/thingmalalisti/?lthing='+str(session)
	response = requests.get(url)
	data = xmltodict.parse(response.text)
	mal = {}
	for m in data[u'málaskrá'][u'mál']:
		mal[m[u'@málsnúmer']] = {'malsnafn': m[u'málsheiti']}
	return mal

session = sys.argv[1]
mal_nefnda = {}
fundartimi_mala = {}
mal = get_mal(session)
malaskra = {}

def laga_tima(timi):
	return timi[0:5].strip()

def get_dagskrarmal(fundargerd):
	dagskrarmal = re.findall('<div.+?>(.+?)</div>',fundargerd)
	results = []
	for mal in dagskrarmal:
		if 'mnr=' in mal:
			mnr = mal.split('mnr=')[1].split('">')[0]
			kl = mal.split('Kl. ')[1]
			results.append([mnr,laga_tima(kl)])
		else: #Til þess að fá upphafstíma á næsta máli ef það er ekki tengt málsnúmeri
			kl = mal.split('Kl. ')[1]
			results.append([None, laga_tima(kl)])
	return results

#Ná í allar fundargerðir

def get_fundartimi_mala(session):
	url = 'http://www.althingi.is/altext/xml/nefndarfundir/?lthing='+str(session)
	response = requests.get(url)
	data = xmltodict.parse(response.text)
	fundartimar = {}
	for fundur in data[u'nefndarfundir'][u'nefndarfundur']:
		try:
			fundur_settur = fundur[u'fundursettur'].split('T')[1]
			fundur_slit = fundur[u'fuslit'].split('T')[1]
			nefnd_id = fundur[u'nefnd'][u'@id']
			nefnd_nafn = fundur[u'nefnd'][u'#text']
			fundargerd = requests.get(fundur[u'nánar'][u'fundargerð'][u'xml'])
			fundargerd_data = xmltodict.parse(fundargerd.text)
			dagskrarmal = get_dagskrarmal(fundargerd_data[u'nefndarfundur'][u'fundargerð'][u'texti'])
			dagskrarmal.append(['fundur_slit', laga_tima(fundur_slit)])
			if nefnd_id in fundartimar:
				fundartimar[nefnd_id]['dagskra'].append(dagskrarmal)
			else:
				fundartimar[nefnd_id] = {}
				fundartimar[nefnd_id]['nafn'] = nefnd_nafn
				fundartimar[nefnd_id]['dagskra'] = [dagskrarmal]
		except Exception as e:
			print(fundur[u'nefnd']['#text'] + ' - ' +  fundur[u'hefst'][u'texti'])
	return fundartimar

fundir = get_fundartimi_mala(session)
#fundir = {'201': {'nafn': 'allsherjar- og menntamálanefnd', 'dagskra': [[[mnr, '10:37'], [...], ...]], [[...], ...]]}}
FMT = '%H:%M'

for nefnd in fundir: #nefnd = nefnd_id
	for fundur in fundir[nefnd]['dagskra']: #[[mnr, '10:37'], [...], ...]], fundur er með mörg dagskrármál
		#finna fundartíma allra mála
		heildartimi = timedelta()
		tdelta = datetime.strptime(fundur[-1][1], FMT) - datetime.strptime(fundur[0][1], FMT)
		heildartimi += tdelta
		fundir[nefnd]['heildartimi'] = str(heildartimi)
		for dagskrarlidur in range(len(fundur)): #fyrir hvern fund um málið [mnr, '10:37']
			mnr, timi = fundur[dagskrarlidur] #hvert mál á fundinum [mnr, tími sem málið er tekið fyrir]
			if mnr:
				if mnr in fundartimi_mala:
					fundartimi_mala[mnr].append([timi,fundur[dagskrarlidur+1][1]]) #[dagskrárliður byrjar, næsti dagskrárliður byrjar]
				else: 
					if mnr != 'fundur_slit':
						if mnr in mal_nefnda:
							mal_nefnda[mnr].append(nefnd)
						else:
							mal_nefnda[mnr] = [nefnd]
						fundartimi_mala[mnr] = [[timi,fundur[dagskrarlidur+1][1]]] #[dagskrárliður byrjar, næsti dagskrárliður byrjar]
			else:
				pass #'None'

heildartimi_allra_mala = timedelta()

for mnr in fundartimi_mala: #yfirfæra heildarfundartíma hvers máls á málsnúmer
	heildartimi = timedelta()
	for fundur in fundartimi_mala[mnr]:
		try:
			tdelta = datetime.strptime(fundur[1], FMT) - datetime.strptime(fundur[0], FMT)
			heildartimi += tdelta
		except:
			print(fundur)
	heildartimi_allra_mala += heildartimi
	mal[str(mnr)]['fundartimi'] = str(heildartimi)

def get_stada_mals(session, mnr):
	stada_mals = ""
	if session in malaskra:
		for m in malaskra[session][u'málaskrá'][u'mál']:
			if m[u'@málsnúmer'] == mnr:
				response = requests.get(m[u'xml'])
				data = xmltodict.parse(response.text)
				stada_mals = data[u'þingmál'][u'mál'][u'staðamáls']
	else:
		url = 'https://www.althingi.is/altext/xml/thingmalalisti/?lthing='+str(session)
		response = requests.get(url)
		malaskra[session] = xmltodict.parse(response.text)
		for m in malaskra[session][u'málaskrá'][u'mál']:
			if m[u'@málsnúmer'] == mnr:
				response = requests.get(m[u'xml'])
				data = xmltodict.parse(response.text)
				stada_mals = data[u'þingmál'][u'mál'][u'staðamáls']
	return stada_mals

#for m in mal:
#	print(m, mal[m])
print(heildartimi_allra_mala)
with open(u'malstimi_'+str(session)+'.txt', 'w') as f:
	f.write('málsnúmer;málsheiti;staða máls;heildartími;nefndir\n')
	for m in mal:
		try:
			stada_mals = ''
			fundartimi = ''
			try:
				stada_mals = get_stada_mals(session, m)
			except:
				pass
			try:
				fundartimi = mal[m]['fundartimi']
			except:
				pass
			f.write(m + ';' + mal[m]['malsnafn'] + ';' + stada_mals + ';' + fundartimi + ';' + '\n')
		except Exception as e:
			print(m,mal[m],'villa')

#for n in fundir:
#	print(fundir[n])
with open(u'nefndatimi_'+str(session)+'.txt', 'w') as f:
	f.write('nefnd_id,nefnd;fjöldi funda;heildarfundartími;fjöldi mála;mnr\n')
	for n in fundir:
		mnr = set()
		for fundur in fundir[n]['dagskra']:
			for d in fundur:
				try:
					mnr.add(str(int(d[0])))
				except:
					pass	
		f.write(str(n) + ';' + fundir[n]['nafn'] + ';' + str(len(fundir[n]['dagskra'])) + ';' + fundir[n]['heildartimi'] + ';' + str(len(mnr)) + ';' + ','.join(list(mnr)) + ';' + '\n')
