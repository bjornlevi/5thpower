# -*- coding: utf-8 -*-

import csv
from includes import *
from datetime import datetime
from time import strptime as to_date

mps = open('mps_in_commitees.csv', 'r') #mp_id
mp_reader = csv.DictReader(mps)

membership = open('commitee_members.csv', 'r') #commitee_id, mp_id
membership_reader = csv.DictReader(membership)

commitee_meetings = open('commitee_meetings.csv', 'r') #commitee_id, meeting_count
commitee_reader = csv.DictReader(commitee_meetings)

#commitee meeting counter data
commitee_counter = {}
for row in commitee_reader:
	commitee_counter[row['commitee_id']] = row['meeting_count']

commitee_attendence = open('commitee_attendence.csv', 'r') #commitee_id, meeting_count
commitee_attendence_reader = csv.DictReader(commitee_attendence)
mp_meeting_attendence = {}
for row in commitee_attendence_reader:
	mp_meeting_attendence[row['mp_id']] = row['meeting_count']

#collect commitees each mp is registered for
mp_commitees = {} #{mp_id: [commitee_id, ...], ...}
for row in membership_reader:
	if row['mp_id'] in mp_commitees:
		mp_commitees[row['mp_id']].append(row['commitee_id'])
	else:
		mp_commitees[row['mp_id']] = [row['commitee_id']]

print "processing expected mp meeting dates"

mp_commitee_meeting_counter = {} #{mp: {commitee_id: meeting_count, ...}, ...}
for mp in mp_commitees:
	print "processing mp", mp
	#count number of meetings mp was expected to attend based on commitee membership
	meeting_dates = get_commitee_meeting_dates(144)
	mp_commitee_membership = get_mp_commitee_membership_dates(mp)
	for commitee in mp_commitee_membership[unicode(144)]:
		#process commitee only if mp is a member (not varamaður or áheyrnarfulltrúi)
		if 'forma' in commitee['position'] or 'nefndarma' in commitee['position']:
			print "processing", commitee['position'], "in commitee", commitee['commitee_id']
			try: #skip commitees that don't have any meetings
				commitee_meeting_dates = meeting_dates[commitee['commitee_id']]
				start = to_date(commitee[u'start'], "%d.%m.%Y")
				if commitee[u'end']:
					end = to_date(commitee[u'end'], "%d.%m.%Y")
				else:
					end = to_date(datetime.now().strftime('%d.%m.%Y'), '%d.%m.%Y')
				for date in commitee_meeting_dates:
					meeting_date = to_date(date, "%Y-%m-%d")
					if start <= meeting_date <= end:
						if mp in mp_commitee_meeting_counter:
							mp_commitee_meeting_counter[mp].append(date)
						else:
							mp_commitee_meeting_counter[mp] = [date]
			except:
				pass
		else:
			#don't count this commitee for required attendance
			print "skipping", commitee['position'], "in commitee", commitee['commitee_id']
			pass

mp_list = get_mp_id_and_short_name(144)
with open('expected_attendence.csv', 'w+') as csvfile:
	data = "mp_id,total_meetings,attended_meetings\n"
	for mp in mp_commitees:
		data += str(mp_list[mp]) + ',' + str(len(mp_commitee_meeting_counter[mp])) + ',' + str(mp_meeting_attendence[mp]) + '\n'
	csvfile.write(data)
