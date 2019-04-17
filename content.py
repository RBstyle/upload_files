import sqlite3
import os

def get_list_uploads():
    uploads_count = []
    for filename in os.listdir('uploads/'):
        uploads_count.append(filename)
    return uploads_count

'''
следующие функции не актуальны.
'''
def connect_db(query=None):
    if query == 'commit':
        con.commit()
        print('Commit exept')
        return None
    con = sqlite3.connect('./data/info.db')
    cur = con.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS incoming_files(Filename TEXT, Url TEXT, IP adress text)')
    return cur

def insert_value(filename, ip):
    print('start')
    cur = connect_db()
    data = [filename, 'uploads/' + filename, ip]
    cur.execute('INSERT INTO incoming_files VALUES(?, ?, ?)', data)
    connect_db('commit')
    print('end')
    return None