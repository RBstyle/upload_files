import sqlite3
con = sqlite3.connect('./data/info.db')
cur = con.cursor()
filename = ['123.txt']
cur.execute('SELECT * FROM incoming_files WHERE Filename=?', filename)
print(filename)
print(cur.fetchone()[2])
cur.close()
con.close()
