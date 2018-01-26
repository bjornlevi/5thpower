import sqlite3
import re

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

conn = sqlite3.connect('ordanotkun.db')
word_conn = sqlite3.connect('words.db')
conn.row_factory = dict_factory
c = conn.cursor()
w = word_conn.cursor()
try:
	#save speech/speaker/session/speech start/speech end
	w.execute('''CREATE TABLE words(word text)''')
except:
	#table exists
	pass

c.execute('SELECT * FROM ordanotkun')
for row in c.fetchall():
	words = re.compile("[\s]+").split(row["speech_text"])
	print(words)
	data = [tuple(word) for word in words]
	print(data)
	w.executemany('INSERT INTO words VALUES (?)', data)
w.commit()
w.close()
c.close()