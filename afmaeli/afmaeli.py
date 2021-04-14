import xmltodict
import requests
from datetime import datetime

def kyn(nafn):
	if(nafn.find(u'dóttir') != -1):
		return 'kvk'
	elif(nafn.find(u'son') != -1):
		return 'kk'
	else:
		return '0'

def kenninafn(nafn):
	if(nafn.find(u'dóttir') != -1):
		return nafn.split(' ')[-1][:-6]
	elif(nafn.find(u'son') != -1):
		return nafn.split(' ')[-1][:-3]
	else:
		return '0'

def most_common(lst):
    return max(set(lst), key=lst.count)

url = 'http://www.althingi.is/altext/xml/thingmenn/'
response = requests.get(url)
data = xmltodict.parse(response.text)

afmaelisdagar = []
mps = []
kenninofn = []
for mp in data[u'þingmannalisti'][u'þingmaður']:
	afmaelisdagar.append([datetime.strptime(mp[u'fæðingardagur'], '%Y-%m-%d'), mp[u'nafn']])
	mps.append((mp[u'nafn'], mp[u'fæðingardagur']))
	kenninofn.append(kenninafn(mp[u'nafn']))

#afmaelisdagar.sort()
for afmaelisdagur in afmaelisdagar:
	print(str(afmaelisdagur[0]) +', '+ afmaelisdagur[1] +', ' + kyn(afmaelisdagur[1]))

print(len(set(mps)))

#while '0' in kenninofn: kenninofn.remove('0')
#print(kenninofn)
mc = most_common(kenninofn)
print(mc, kenninofn.count(mc))