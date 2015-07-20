# -*- coding: utf-8 -*-

import csv
from nefndarfundir import *

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
mp_commitees = {}
for row in membership_reader:
	if row['mp_id'] in mp_commitees:
		mp_commitees[row['mp_id']].append(row['commitee_id'])
	else:
		mp_commitees[row['mp_id']] = [row['commitee_id']]

#collect number of meetings each mp should attend
mp_expected_attendence = {}
not_registered_commitees = {}
for mp in mp_commitees:
	for commitee_id in mp_commitees[mp]:
		try:
			#sum up total meetings for all commitees
			if mp in mp_expected_attendence:
				mp_expected_attendence[mp] += int(commitee_counter[commitee_id])
			else:
				mp_expected_attendence[mp] = int(commitee_counter[commitee_id])
		except:
			#log commitees that have no meeting data
			if mp in not_registered_commitees:
				not_registered_commitees[mp].append(commitee_id)
			else:
				not_registered_commitees[mp] = [commitee_id]

mp_list = get_mp_id_and_short_name(144)
with open('expected_attendence.csv', 'w+') as csvfile:
	data = "mp_id,total_meetings,attended_meetings\n"
	for mp in mp_expected_attendence:
		data += str(mp_list[mp]) + ',' + str(mp_expected_attendence[mp]) + ',' + str(mp_meeting_attendence[mp]) + '\n'
	csvfile.write(data)