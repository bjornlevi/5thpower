# -*- coding: utf-8 -*-

import requests
import xmltodict
from datetime import datetime

def get_skjal(url):
    """
    returns appropriate document in parsed xmldict
    """
    response = requests.get(url)
    return xmltodict.parse(response.text)


def get_flutningsmadur(url):
    """
    returns {'id': flutningsmadur_id, 'nafn': flutningsmadur_nafn}
    """
    response = requests.get(url)
    data = xmltodict.parse(response.text)
    for skjal in data[u'þingmál'][u'þingskjöl'][u'þingskjal']:
        if skjal[u'skjalategund'] == 'fsp. til skrifl. svars':
            document = get_skjal(skjal[u'slóð'][u'xml'])
            try:
                if len(document[u'þingskjal'][u'þingskjal'][u'flutningsmenn']) == 1:
                    return {
                        'id': document[u'þingskjal'][u'þingskjal'][u'flutningsmenn'][u'flutningsmaður'][u'@id'],
                        'nafn': document[u'þingskjal'][u'þingskjal'][u'flutningsmenn'][u'flutningsmaður'][u'nafn']
                    }
                else:
                    return {
                        'id': document[u'þingskjal'][u'þingskjal'][u'flutningsmenn'][0][u'flutningsmaður'][u'@id'],
                        'nafn': document[u'þingskjal'][u'þingskjal'][u'flutningsmenn'][0][u'flutningsmaður'][u'nafn']
                    }
            except:
                return None          
    return None

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
                    'question_date': doc[u'útbýting'],
                    'question_by': get_flutningsmadur(data[u'þingmál'][u'mál'][u'slóð'][u'xml']),
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

sessions = list(range(144,145))

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

    ministers = {}

    for i in issues:
        try:
            print('Processing: ' + str(issues[i]['question']['question_id']))
        except:
            pass
        if issues[i]['question'] == '':
            #issue has been dropped
            pass
        elif issues[i]['answer'] == '':
            #question has not been answered
            #print(issues[i]['question']['question_date'] + ', ' + issues[i]['question']['question_name'] + ', ' + issues[i]['question']['question_to'] + ', ' + issues[i]['question']['url'])
            date1 = datetime.strptime(issues[i]['question']['question_date'], '%Y-%m-%d %H:%M')
            date2 = datetime.now()
            unanswered.append(abs(date2-date1).days)
            if issues[i]['issue_minister'] in ministers:
                ministers[issues[i]['issue_minister']]['unanswered'].append(abs(date2-date1).days)
                try:
                    ministers[issues[i]['issue_minister']]['question_by'].append(issues[i]['question']['question_by']['nafn'])
                except:
                    pass
            else:
                ministers[issues[i]['issue_minister']] = {
                    'unanswered': [abs(date2-date1).days],
                    'answered': [],
                    'question_by': [issues[i]['question']['question_by']['nafn']]
                }
        else:
            #question has been answered
            date1 = datetime.strptime(issues[i]['question']['question_date'], '%Y-%m-%d %H:%M')
            date2 = datetime.strptime(issues[i]['answer']['answer_date'], '%Y-%m-%d %H:%M')
            answered.append(abs(date2-date1).days)
            if issues[i]['issue_minister'] in ministers:
                ministers[issues[i]['issue_minister']]['answered'].append(abs(date2-date1).days)
                try:
                    ministers[issues[i]['issue_minister']]['question_by'].append(issues[i]['question']['question_by']['nafn'])
                except:
                    pass
            else:
                ministers[issues[i]['issue_minister']] = {
                    'answered': [abs(date2-date1).days],
                    'unanswered': [],
                    'question_by': [issues[i]['question']['question_by']['nafn']]
                }

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

    print('Þing: ' + str(session))
    print('Meðalfjöldi virka daga v/ósvaraðra spurninga: ' + str(round(u)) + ' / fjöldi ósvaraðra fyrirspurna: ' + str(len(unanswered)))
    print('Meðalsvartími í virkum dögum: ' + str(round(a)) + ' / fjöldi svaraðra fyrirspurna: ' + str(len(answered)))
    print('Heildarfjöldi fyrirspurna: ' + str(len(answered)+len(unanswered)))
    print('===')
    
    print('Svartími einstaka ráðherra')
    for m in ministers:
        u = 0
        a = 0
        try:
            u = sum(ministers[m]['unanswered'])/len(ministers[m]['unanswered'])*5/7
        except:
            pass
        try:
            a = sum(ministers[m]['answered'])/len(ministers[m]['answered'])*5/7
        except:
            pass

        print(m)
        print('Meðalfjöldi virka daga v/ósvaraðra spurninga: ' + str(round(u)) + ' / fjöldi ósvaraðra fyrirspurna: ' + str(len(ministers[m]['unanswered'])))
        print('Meðalsvartími í virkum dögum: ' + str(round(a)) + ' / fjöldi svaraðra fyrirspurna: ' + str(len(ministers[m]['answered'])))
        print('Heildarfjöldi fyrirspurna: ' + str(len(ministers[m]['answered'])+len(ministers[m]['unanswered'])))
        for question_by in ministers[m]['question_by']:
            print(question_by)
        print('===')        