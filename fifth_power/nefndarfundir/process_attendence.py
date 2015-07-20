# -*- coding: utf-8 -*-

import csv

mps = open('mps_in_commitees.csv', 'r') #mp_short_name
mp_fieldnames = ['mp_short_name']
mp_reader = csv.DictReader(mps, mp_fieldnames)

membership = open('commitee_members.csv', 'r') #commitee_id, mp_short_name
membership_fieldnames = ['commitee_id', 'mp_short_name']
membership_reader = csv.DictReader(membership, membership_fieldnames)

commitee_meetings = open('commitee_meetings.csv', 'r') #commitee_id, meeting_count
commitee_fieldnames = ['commitee_id', 'meeting_count']
commitee_reader = csv.DictReader(commitee_meetings, commitee_fieldnames)

#commitee meeting counter data
commitee_counter = {}
for row in commitee_reader:
	commitee_counter[row['commitee_id']] = row['meeting_count']

#collect commitees each mp is registered for
mp_commitees = {}
for row in membership_reader:
	if row['mp_short_name'] in mp_commitees:
		mp_commitees[row['mp_short_name']].append(row['commitee_id'])
	else:
		mp_commitees[row['mp_short_name']] = [row['commitee_id']]

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
				mp_expected_attendence[mp].append(commitee_id)
			else:
				mp_expected_attendence[mp] = [commitee_id]

for mp in mp_expected_attendence:
	print mp.encode('utf-8', 'ignore') + ',' + str(mp_expected_attendence[mp])