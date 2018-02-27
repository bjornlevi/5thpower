# -*- coding: utf-8 -*-

sessions = list(range(108,149))

skyrslubeidni = open('skyrslubeidni', 'w')
for s in sessions:
	try:
		with open(str(s), 'r') as f:
			for line in f:
				l = line.split(';')
				if l[3] == 'b':
					skyrslubeidni.write(l[1] + ';' + l[2] + '\n')
	except:
		pass
	
skyrslubeidni.close()
	
#f = open(str(session), 'w')