'''Задача: требуется сделать сервис, который позволяет закачать (upload) файл на сервер и отдать ссылку по которой этот файл можно скачать. 
Ограничение - скачать можно только с того же самого IP адреса, с которого он был закачен.'''

from flask import Flask, request, send_file, render_template, request, send_from_directory , redirect, jsonify
from werkzeug import utils
from werkzeug.utils import secure_filename
import os
import sqlite3
from content import get_list_uploads, connect_db, insert_value
app = Flask(__name__)

@app.route("/")
def home():
    ip=request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    return render_template('index.html', ip=ip)

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        ip=request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        f = request.files['file']
        filename = secure_filename(f.filename)
        #insert_value(filename, ip)
        con = sqlite3.connect('./data/info.db')
        cur = con.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS incoming_files(Filename TEXT, Url TEXT, IP adress text)')
        data = [filename, 'uploads/' + filename, ip]
        cur.execute('INSERT INTO incoming_files VALUES(?, ?, ?)', data)
        con.commit()
        f.save('uploads/' + filename)
        return redirect('/upllist')
    return render_template('upload_file.html')


@app.route('/upllist', methods=['GET', 'POST'])
def upllist():
    if request.method == 'POST':
        filename = request.form['filename']
        #connect_db()
        con = sqlite3.connect('./data/info.db')
        cur = con.cursor()
        name =[filename]
        cur.execute('SELECT * FROM incoming_files WHERE Filename=?', name)
        key_ip = cur.fetchone()[2]
        ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        if key_ip == ip:
            return send_file('uploads/' + filename, as_attachment=True)
        return redirect('/')
    return render_template('upllist.html', uploads_count=get_list_uploads())

@app.route('/download/<filename>', methods=['GET', 'POST'])
def download(filename):
    return render_template('download.html', namefail=filename)

if __name__ == '__main__':
    '''con = sqlite3.connect('./data/info.db')
    cur = con.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS incoming_files(Filename TEXT, Url TEXT, IP adress text)')'''
    app.run()
    