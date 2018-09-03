import sqlite3
from collections import OrderedDict
import re

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

conn = sqlite3.connect('ordanotkun.db')
conn.row_factory = dict_factory
c = conn.cursor()

word_dict = {}

c.execute('SELECT * FROM ordanotkun')
for row in c.fetchall():
	words = re.sub('[^\u00d8-\u00f6A-Za-z0-9þæðöúíóý\s]+', '', row["speech_text"])
	words = re.compile("[\s]+").split(words)
	for word in words:
		if word in word_dict:
			word_dict[word] += 1
		else:
			word_dict[word] = 1

word_dict = OrderedDict(sorted(word_dict.items(), key=lambda t: t[1]))
with open('words.txt', 'w') as f:
	for word in word_dict:
		f.write(word +','+ str(word_dict[word]) + '\n')