from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data/test2.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Заменить на config.upload
db = SQLAlchemy(app)


class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(256), unique=False, nullable=False)
    url = db.Column(db.String(1024), unique=True, nullable=False)
    ip_address = db.Column(db.String(64), unique=False, nullable=True)

    def __init__(self, filename, url, ip_address):
        self.filename = filename
        self.url = url
        self.ip_address = ip_address

    '''def __repr__(self):
        return '<File %r>' % self.filename'''


if __name__ == "__main__":
    db.create_all()
    # file1 = File('file4.txt', '/upload/file4.txt', '1.2.3.44')
    # db.session.add(file1)
    # db.session.commit()
    file = File.query.filter_by(ip_address='1.2.3.44').first()
    print(file.url)
