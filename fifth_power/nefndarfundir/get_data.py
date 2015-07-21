# -*- coding: utf-8 -*-
from includes import *
import sys

if len(sys.argv) == 2:
	#good
	pass
else:
	if sys.argv[1] == '--help':
		print "get_data.py session_nr\n"
		print "get_data.py 144"
	else:
		print "incorrect number of arguments, must provide session number"

# ! --- SAVE OUTPUT ---

print "Processing commitee members"
commitee_membership = get_mp_commitees(144)
commitee_members = get_commitee_members([commitee_membership[i] for i in commitee_membership])

print "Saving commitee membership"

#mps registered as commitee members
with open('mps_in_commitees.csv', 'w+') as csvfile:
	data = "mp_id\n"
	for member in commitee_members:
		data += member + '\n'
	csvfile.write(data)

#mps registered as commitee members
with open('commitee_members.csv', 'w+') as csvfile:
	data = "commitee_id,mp_id\n"
	for commitee in commitee_membership:
		for member in commitee_membership[commitee]:
			data += commitee.encode('utf-8', 'ignore') + "," + member.encode('utf-8', 'ignore') + '\n'
	csvfile.write(data)

print "Processing meeting attendence"

#count number of meetings in each commitee
meeting_dates = get_commitee_meetings_attendence(144)

with open('commitee_attendence.csv', 'w+') as csvfile:
	data = "mp_id,meeting_count\n"
	mp_commitee_membership = {}
	for mp in meeting_dates:
		#for meeting in meeting_dates[mp]: #to list all meetings attended
			#mp, commitee_id, meeting_id
			#data += mp + ',' + str(meeting[0]) + ',' + str(meeting[1]) + '\n'
		#mp, number of meetings
		data += mp + ',' + str(len(meeting_dates[mp])) + '\n' #to only count number of meetings for each mp
	csvfile.write(data)

with open('commitee_attendence_dates.csv', 'w+') as csvfile:
	data = "mp,commitee_id,meeting_id,meeting_date\n"
	mp_commitee_membership = {}
	for mp in meeting_dates:
		for meeting in meeting_dates[mp]: #to list all meetings attended
			#mp,commitee_id,meeting_id,meeting_date
			data += mp + ',' + str(meeting[0]) + ',' + str(meeting[1]) + ',' + str(meeting[2]) + '\n'
	csvfile.write(data)

print "processing commitee meeting count"

#count number of meetings for each commitee
commitee_meetings = get_commitee_meeting_dates(144)
with open('commitee_meetings.csv', 'w+') as csvfile:
	data = "commitee_id,meeting_count\n"
	for meeting in commitee_meetings:
		data += meeting.encode('utf-8', 'ignore') + "," + str(len(commitee_meetings[meeting])) + '\n'
	csvfile.write(data)
