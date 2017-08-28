# -*- coding: utf-8 -*-

import requests
import xmltodict
from datetime import datetime

def get_documents(url):
	"""
	returns {'question_id': x, 'question_date':y}
	"""
	response = requests.get(url)
	data = xmltodict.parse(response.text)
	issue_status = data[u'þingmál'][u'mál'][u'staðamáls']
	issue_minister = data[u'þingmál'][u'mál'][u'fyrirspurntil']
	question = ''
	answer = ''
	if issue_status == 'Fyrirspurninni var svarað skriflega.':
		for doc in data[u'þingmál'][u'þingskjöl'][u'þingskjal']:
			if doc[u'skjalategund'] == 'svar':
				answer = {
					'answer_id': doc[u'@skjalsnúmer'], 
					'answer_date': doc[u'útbýting']
				}
			else:
				question = {
					'question_id': doc[u'@skjalsnúmer'], 
					'question_date': doc[u'útbýting']
				}
	elif issue_status == 'Fyrirspurninni hefur ekki verið svarað.' or issue_status == 'Fyrirspurninni var ekki svarað.':
			question = {
				'question_id': data[u'þingmál'][u'þingskjöl'][u'þingskjal'][u'@skjalsnúmer'], 
				'question_date': data[u'þingmál'][u'þingskjöl'][u'þingskjal'][u'útbýting'],
				'question_name': data[u'þingmál'][u'mál'][u'málsheiti'],
				'question_to': data[u'þingmál'][u'mál'][u'fyrirspurntil'],
				'url': data[u'þingmál'][u'mál'][u'slóð'][u'html']
			}	
	
	return {
		'issue_status': issue_status,
		'issue_minister': issue_minister,
		'question': question,
		'answer': answer
		}

sessions = list(range(146,147))

url = "http://www.althingi.is/altext/xml/thingmalalisti/?lthing="

for session in sessions:
	query = url+str(session)
	response = requests.get(query)
	#print response.text.encode('utf-8', 'ignore')
	data = xmltodict.parse(response.text)

	issues = {}
	for issue in data[u'málaskrá'][u'mál']:
		issue_id = issue[u'@málsnúmer']
		if issue[u'málstegund']['@málstegund'] == 'q':
			issues[issue_id] = get_documents(issue[u'xml'])


	unanswered = []
	answered = []

	for i in issues:
		if issues[i]['question'] == '':
			#issue has been dropped
			pass
		elif issues[i]['answer'] == '':
			#question has not been answered
			print(issues[i]['question']['question_date'] + ', ' + issues[i]['question']['question_name'] + ', ' + issues[i]['question']['question_to'] + ', ' + issues[i]['question']['url'])
			date1 = datetime.strptime(issues[i]['question']['question_date'], '%Y-%m-%d %H:%M')
			date2 = datetime.now()
			unanswered.append(abs(date2-date1).days)
		else:
			#question has been answered
			date1 = datetime.strptime(issues[i]['question']['question_date'], '%Y-%m-%d %H:%M')
			date2 = datetime.strptime(issues[i]['answer']['answer_date'], '%Y-%m-%d %H:%M')
			answered.append(abs(date2-date1).days)

	u = 0
	a = 0
	try:
		u = sum(unanswered)/len(unanswered)*5/7
	except:
		pass
	try:
		a = sum(answered)/len(answered)*5/7
	except:
		pass

	print('Þing: ' + str(session) + '; Meðalfjöldi virka daga: ' + str(round(u)) + ' / fjöldi ósvaraðra fyrirspurna: ' + str(len(unanswered)) + '. Meðalsvartími í virkum dögum: ' + str(round(a)) + ' / fjöldi svaraðra fyrirspurna: ' + str(len(answered)))
	#print( str(a) 