'''Задача: требуется сделать сервис, который позволяет закачать (upload) файл на сервер и отдать ссылку по которой этот файл можно скачать. 
Ограничение - скачать можно только с того же самого IP адреса, с которого он был закачен.'''

from flask import Flask, request, send_file, render_template, request, send_from_directory , redirect, jsonify
from werkzeug import utils
from werkzeug.utils import secure_filename
import os
import sqlite3
from flask_sqlalchemy import SQLAlchemy
from content import get_list_uploads, connect_db, insert_value

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)
db.create_all()

class IncommingFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(256), unique=False, nullable=False)
    url = db.Column(db.String(1024), unique=True, nullable=False)
    ip_address = db.Column(db.String(64), unique=False, nullable=True)

    def __repr__(self):
        return '<File %r>' % self.filename

@app.route("/")
def home():
    ip=request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    # проверка на морде на определение ip адреса для наглядности
    return render_template('index.html', ip=ip)

'''

декоратор загрузки файла.
'''
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        ip=request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        # честно спизженно с  https://gist.github.com/ruanbekker/b745d6cb3bf56d4105f08b19eac6d8fc
        f = request.files['file']
        filename = secure_filename(f.filename)
        # проверка безопасности имени файла
        # здесь должна быть проверка на наличие такого же фалйа в базе
        con = sqlite3.connect('./data/info.db')
        cur = con.cursor()
        cur.execute('CREATE TABLE IF NOT EXISTS incoming_files(Filename TEXT, Url TEXT, IP adress text)')
        # коннектимся к БД, создаем таблицу для данных(если ее еще нет)
        data = [filename, 'uploads/' + filename, ip]
        cur.execute('INSERT INTO incoming_files VALUES(?, ?, ?)', data)
        con.commit()
        # прикрутить проверку на успешное внесение изменений в БД перед загрузкой        
        f.save('uploads/' + filename)
        return redirect('/upllist')
    return render_template('upload_file.html')

'''

декоратор списка доступных файлов(отображение ссылки на скачивание в /upllist)
'''
@app.route('/upllist', methods=['GET', 'POST'])
def upllist():
    if request.method == 'POST':
        filename = request.form['filename']
        con = sqlite3.connect('./data/info.db')
        cur = con.cursor()
        name =[filename]
        cur.execute('SELECT * FROM incoming_files WHERE Filename=?', name)
        key_ip = cur.fetchone()[2]
        # достаем ip адресс закрепленный за файлом. Способ извлечение конкретного значения из БД сомнительный
        # но лучшего не придумал
        ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        if key_ip == ip:
            return send_file('uploads/' + filename, as_attachment=True)
        return redirect('/')
        # проверка на право доступа и отправка файла
    return render_template('upllist.html', uploads_count=get_list_uploads())

'''

декоратор доступа к скачиванию
'''
@app.route('/download/<filename>', methods=['GET', 'POST'])
def download(filename):
    return render_template('download.html', namefail=filename)

if __name__ == '__main__':
    '''con = sqlite3.connect('./data/info.db')
    cur = con.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS incoming_files(Filename TEXT, Url TEXT, IP adress text)')'''
    app.run()
    
