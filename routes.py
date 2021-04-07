from flask import Flask, request, jsonify, render_template, redirect, make_response
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from flask_restful import Resource
from models import User, Message, Tweet
from db import db

class Index(Resource):
    def get(self):
        if current_user.is_authenticated:
            return "Hello, " + current_user.get_username() + "!"
        else:
            return "Hello, please register or login!"

class Users(Resource):
    def get(self):
        users = User.query.all()
        return jsonify([{"username": user.username, "password_hash": user.password_hash, "id": user.id} for user in users])

class Register(Resource):
    def get(self):
        if current_user.is_authenticated:
            return redirect('/')
        headers = {'Content-Type': 'text/html'}
        return make_response(render_template('register.html'), 200, headers)

    def post(self):
        username = request.form['username']
        password = request.form['password']
        password2 = request.form['password2']

        if not (username and password and password2):
            return {'error': 'Fields are required to be filled.'}, 400

        else:
            if password != password2:
                return {'error': 'Password mismatch!'}, 401

            if User.query.filter_by(username=username).first():
                return {'error': 'User exists, try another username!'}, 409

            user = User(username=username, password=password)
            db.session.add(user)
            db.session.commit()
            return redirect('/login')


class Login(Resource):
    def get(self):
        if current_user.is_authenticated:
            return redirect('/')
        headers = {'Content-Type': 'text/html'}
        return make_response(render_template('login.html'), 200, headers)

    def post(self):
        username = request.form['username']
        password = request.form['password']

        if not (username and password):
            return {'error': 'Fields are required to be filled.'}, 400

        else:
            user = User.query.filter_by(username = username).first()
            if user is not None:
                if user.check_password(password):
                    login_user(user)
                    return redirect('/')
                else:
                    return {'error': 'Incorrect password!'}, 401
            else:
                return {'error':'Cannot find user with username ' + username}, 404

class Logout(Resource):
    def get(self):
        logout_user()
        return redirect('/')

class Chat(Resource):
    @login_required
    def get(self):
        headers = {'Content-Type': 'text/html'}
        return make_response(render_template('chat.html'), 200, headers)

    @login_required
    def post(self):
        _from = current_user.get_username()
        _to = request.form['_to']
        content = request.form['content']
        if (_to and content):
            if User.query.filter_by(username=_to).first():
                message = Message(_from=_from, _to=_to, content=content)
                db.session.add(message)
                db.session.commit()
                return {'success': 'Message has been sent!'}, 200
            else:
                return {'error':'Cannot find user with username ' + _to}, 404
        else:
            return {'error': 'Fields are required to be filled.'}, 400

class SentHistory(Resource):
    @login_required
    def get(self):
        _from = current_user.get_username()
        messages = Message.query.filter_by(_from=_from)
        return jsonify([{'_to': m._to, 'message': m.content} for m in messages])

class ReceivedHistory(Resource):
    @login_required
    def get(self):
        _to = current_user.get_username()
        messages = Message.query.filter_by(_to=_to)
        return jsonify([{'_from': m._from, 'message': m.content} for m in messages])

class Tweets(Resource):
    @login_required
    def get(self):
        tweets = Tweet.query.all()
        username = current_user.get_username()
        return jsonify([{"author": username, "tweet_id": t.id, "title": t.title, "content": t.content, "like": t.like} for t in tweets])

    @login_required
    def post(self):
        uid = current_user.get_id()
        user = User.query.filter_by(id = uid).first()
        title = request.form["title"]
        content = request.form["content"]
        like = 0
        if (title and content):
            tweet = Tweet(user, title, content, like)
            db.session.add(tweet)
            db.session.commit()
            return {'success': 'Tweet has been posted!'}, 200
        else:
            return {'error': 'Fields are required to be filled.'}, 400

    @login_required
    def put(self):
        uid = current_user.get_id()
        user = User.query.filter_by(id = uid).first()
        tweet_id = request.form["tweet_id"]
        title = request.form["title"]
        content = request.form["content"]
        if (tweet_id and title and content):
            tweet = Tweet.query.filter_by(id = tweet_id).first()
            if tweet is not None:
                tweet.title = title
                tweet.content = content
                db.session.commit()
                return {'success': 'Tweet has been updated!'}, 200
            else:
                return {'error': 'Tweet Not Found.'}, 404
        else:
            return {'error': 'Fields are required to be filled.'}, 400

    @login_required
    def delete(self):
        tweet_id = request.form["tweet_id"]
        if tweet_id:
            tweet = Tweet.query.filter_by(id = tweet_id).first()
            if tweet is not None:
                db.session.delete(tweet)
                db.session.commit()
                return {'success': 'Tweet has been deleted!'}, 200
            else:
                return {'error': 'Tweet Not Found'}, 404
        else:
            return {'error': 'Fields are required to be filled.'}, 400

class Like(Resource):
    def post(self):
        tweet_id = request.form["tweet_id"]
        if tweet_id:
            tweet = Tweet.query.filter_by(id = tweet_id).first()
            if tweet is not None:
                current_like = tweet.like+1
                tweet.like = current_like
                db.session.commit()
                return {'success': 'Liked the Tweet! Like count is now '+ str(current_like) + '!'}, 200
            else:
                return {'error': 'Tweet Not Found'}, 404
        else:
            return {'error': 'Fields are required to be filled.'}, 400

class Unlike(Resource):
    def post(self):
        tweet_id = request.form["tweet_id"]
        if tweet_id:
            tweet = Tweet.query.filter_by(id = tweet_id).first()
            if tweet is not None:
                current_like = tweet.like-1
                tweet.like = current_like
                db.session.commit()
                return {'success': 'Unliked the Tweet! Like count is now '+ str(current_like) + '!'}, 200
            else:
                return {'error': 'Tweet Not Found'}, 404
        else:
            return {'error': 'Fields are required to be filled.'}, 400

def initialize_routes(api):
    api.add_resource(Users, '/users')
    api.add_resource(Index, '/')
    api.add_resource(Register, '/register')
    api.add_resource(Login, '/login')
    api.add_resource(Logout, '/logout')
    api.add_resource(Chat, '/chat')
    api.add_resource(SentHistory, '/history/sent')
    api.add_resource(ReceivedHistory, '/history/received')
    api.add_resource(Tweets, '/tweet')
    api.add_resource(Like, '/like')
    api.add_resource(Unlike, '/unlike')
