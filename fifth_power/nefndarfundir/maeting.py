# -*- coding: utf-8 -*-

import json

with open('nefndarfundir.js') as data_file:    
	data = json.load(data_file)

short_names = {}

for meeting in data:
	try:
		for short_name in data[meeting]['short_names']:
			if short_name in short_names:
				short_names[short_name] += 1
			else:
				short_names[short_name] = 1
	except Exception as e:
		pass

print short_names

for name in short_names:
	print name.encode('utf-8') + ';' + str(short_names[name])