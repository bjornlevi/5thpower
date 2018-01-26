import sqlite3

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

conn = sqlite3.connect('ordanotkun.db')
conn.row_factory = dict_factory
c = conn.cursor()

c.execute('SELECT * FROM ordanotkun')
for row in c.fetchall():
	print(row["session"])