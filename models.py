from flask import jsonify
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from db import db

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(16), unique=True)
    password_hash = db.Column(db.String(128))

    def __init__(self, username, password):
        self.username = username
        self.password_hash = generate_password_hash(password)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_username(self):
        return self.username

    def get_id(self):
        return self.id

class Message(db.Model):
    __tablename__ = 'message'
    id = db.Column(db.Integer, primary_key=True)
    _from = db.Column(db.String(16))
    _to = db.Column(db.String(16))
    content = db.Column(db.String(128))

    def __init__(self, _from, _to, content):
        self._from = _from
        self._to = _to
        self.content = content

class Tweet(db.Model):
    __tablename__ = 'tweet'
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, db.ForeignKey("user.id"))
    user = db.relationship('User', foreign_keys=uid)
    title = db.Column(db.String(64))
    content = db.Column(db.String(128))

    def __init__(self, user, title, content):
        self.user = user
        self.title = title
        self.content = content
