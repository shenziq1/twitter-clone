from flask import Flask, request, jsonify, render_template, redirect, make_response
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from flask_restful import Resource
from models import User, Message, Tweet
from db import db

class Index(Resource):
    def get(self):
        # is_authenticated means that current_user is successfully logged in.
        if current_user.is_authenticated:
            return 'Hello, ' + current_user.get_username() + '!'
        else:
            return 'Hello, please register or login!'

# This route is for the purpose of debugging
class Users(Resource):
    def get(self):
        users = User.query.all()
        return jsonify([{'username': user.username, 'password_hash': user.password_hash, 'id': user.id} for user in users])

class Register(Resource):
    def get(self):
        # A logged in user will be redirect to home page
        if current_user.is_authenticated:
            return redirect('/')
        headers = {'Content-Type': 'text/html'}
        return make_response(render_template('register.html'), 200, headers)

    def post(self):
        username = request.form['username']
        password = request.form['password']
        password2 = request.form['password2']

        # This case is when the form is not completed.
        if not (username and password and password2):
            return {'error': 'Fields are required to be filled.'}, 400

        else:
            # This case is when user inputs two different passwords. Two
            # passwords must be identical to prevent mistyping.
            if password != password2:
                return {'error': 'Password mismatch!'}, 401

            # This case is when user registers a username that already exists
            # in the database
            if User.query.filter_by(username=username).first():
                return {'error': 'User exists, try another username!'}, 409

            # This case is when a user is successfully registered,
            # and its information will be stored in the database.
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

            # This case is to check if a user's username is in the database.
            if user is not None:

                # Then check if its password is correct.
                if user.check_password(password):

                    # Log this user in by login_user provided by flask_login
                    login_user(user)
                    return redirect('/')
                else:
                    return {'error': 'Incorrect password!'}, 401
            else:
                return {'error':'Cannot find user with username ' + username}, 404

class Logout(Resource):
    def get(self):
        # Log this user out by logout_user provided by flask_login
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

# This endpoint is to check all the messages that current user has sent.
class SentHistory(Resource):
    @login_required
    def get(self):
        _from = current_user.get_username()
        # Get all messages in database whose _from field is current_user's username.
        messages = Message.query.filter_by(_from=_from)
        return jsonify([{'_to': m._to, 'message': m.content} for m in messages])

# This endpoint is to check all the messages that current user has received.
class ReceivedHistory(Resource):
    @login_required
    def get(self):
        _to = current_user.get_username()
        # Get all messages in database whose _to field is current_user's username.
        messages = Message.query.filter_by(_to=_to)
        return jsonify([{'_from': m._from, 'message': m.content} for m in messages])

class Tweets(Resource):
    @login_required
    def get(self):
        tweets = Tweet.query.all()
        username = current_user.get_username()
        return jsonify([{'author': username, 'tweet_id': t.id, 'title': t.title, 'content': t.content, 'like': t.like} for t in tweets])

    @login_required
    def post(self):
        # Get uid through current_user.
        uid = current_user.get_id()

        # Find this user in database. Note that this user must exists in the database,
        # because when we log in this user, its information is already checked in
        # the database.
        user = User.query.filter_by(id = uid).first()

        # Get those information to create a new Tweet.
        title = request.form['title']
        content = request.form['content']
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

        # This is very similar to the post method, except we need to find the tweet_id
        # we want to update.
        tweet_id = request.form['tweet_id']
        title = request.form['title']
        content = request.form['content']
        if (tweet_id and title and content):
            tweet = Tweet.query.filter_by(id = tweet_id).first()
            if tweet is not None:

                # Update this Tweet
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
        tweet_id = request.form['tweet_id']
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

# Note that this function is not fully implemented yet. If I had more time,
# I will add another field 'liked_user' to the Tweet model, which contains all
# user ids for those who like this Tweet. Then if a user is in the 'liked_user'
# field, then he is not allowed to like this Tweet again.
class Like(Resource):
    def post(self):
        tweet_id = request.form['tweet_id']
        if tweet_id:
            tweet = Tweet.query.filter_by(id = tweet_id).first()
            if tweet is not None:

                # Add one more like to this Tweet.
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
        tweet_id = request.form['tweet_id']
        if tweet_id:
            tweet = Tweet.query.filter_by(id = tweet_id).first()
            if tweet is not None:
                # Subtract one more like from this Tweet.
                current_like = tweet.like-1
                tweet.like = current_like
                db.session.commit()
                return {'success': 'Unliked the Tweet! Like count is now '+ str(current_like) + '!'}, 200
            else:
                return {'error': 'Tweet Not Found'}, 404
        else:
            return {'error': 'Fields are required to be filled.'}, 400

# Add resource to api to initialize routes.
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
