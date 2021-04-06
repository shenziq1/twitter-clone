from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from db import db

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True)
    password_hash = db.Column(db.String(128))

    def __init__(self, username, password):
        self.username = username
        self.password_hash = generate_password_hash(password)

    def get_username(self):
        return self.username

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    _from = db.Column(db.String(20))
    _to = db.Column(db.String(20))
    content = db.Column(db.String(128))

    def __init__(self, _from, _to, content):
        self._from = _from
        self._to = _to
        self.content = content

    def get_content(self):
        return self.content

    def get_from(self):
        return self._from

    def get_to(self):
        return self._to
