'''Задача: требуется сделать сервис, который позволяет закачать (upload) файл
на сервер и отдать ссылку по которой этот файл можно скачать.
Ограничение - скачать можно только с того же самого IP адреса,
с которого он был закачен.'''

from flask import (Flask, request, send_file, render_template, request,
                   redirect, jsonify, url_for)
from werkzeug import utils
from werkzeug.utils import secure_filename
import os
import sqlite3
from flask_sqlalchemy import SQLAlchemy
from content import get_list_uploads

app = Flask(__name__)
app.config.update(
    SQLALCHEMY_DATABASE_URI='sqlite:///data/test.db',
    SQLALCHEMY_TRACK_MODIFICATIONS=False
)
db = SQLAlchemy(app)


class IncommingFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(256), unique=False, nullable=False)
    url = db.Column(db.String(1024), unique=True, nullable=False)
    ip_address = db.Column(db.String(64), unique=False, nullable=True)

    def __repr__(self):
        return '<File %r>' % self.filename

    def __init__(self, filename, url, ip_address):
        self.filename = filename
        self.url = url
        self.ip_address = ip_address


@app.route("/")
def home():
    ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    # проверка на морде на определение ip адреса для наглядности
    return render_template('index.html', ip=ip)

'''

декоратор загрузки файла.
'''


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        # честно спизженно с
        # https://gist.github.com/ruanbekker/b745d6cb3bf56d4105f08b19eac6d8fc
        f = request.files['file']
        filename = secure_filename(f.filename)
        # проверка безопасности имени файла
        # здесь должна быть проверка на наличие такого же фалйа в базе
        uplod_file = IncommingFile(filename,
                                   url_for('download', filename=filename,
                                           _external=True),
                                   ip)
        db.session.add(uplod_file)
        db.session.commit()
        # прикрутить проверку на успешное внесение
        # изменений в БД перед загрузкой
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
        file = IncommingFile.query.filter_by(filename=filename).first()
        key_ip = file.ip_address
        # Достаем ip адресс закрепленный за файлом
        ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        if key_ip == ip:
            return send_file('uploads/' + filename, as_attachment=True)
        return redirect('/')
        # Проверка на право доступа и отправка файла
    return render_template('upllist.html', uploads_count=get_list_uploads())

'''

декоратор доступа к скачиванию
'''


@app.route('/download/<filename>', methods=['GET', 'POST'])
def download(filename):
    return render_template('download.html', namefail=filename)

if __name__ == '__main__':
    app.run()
    db.create_all()
