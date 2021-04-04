from flask import Flask, request, jsonify, render_template, redirect, make_response
from flask_login import LoginManager, UserMixin, current_user, login_user, logout_user, login_required
from flask_restful import Resource
from models import User
from db import db

class IndexApi(Resource):
    def get(self):
        if current_user.is_authenticated:
            return "Hello, " + current_user.get_username() + "!"
        else:
            return "Hello, please register or login!"

class UsersApi(Resource):
    def get(self):
        users = User.query.all()
        return jsonify([{"username": user.username, "password_hash": user.password_hash, "id": user.id} for user in users])

class RegisterApi(Resource):

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


class LoginApi(Resource):
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

class LogoutApi(Resource):
    def get(self):
        logout_user()
        return redirect('/')

def initialize_routes(api):
    api.add_resource(UsersApi, '/users')
    api.add_resource(IndexApi, '/')
    api.add_resource(RegisterApi, '/register')
    api.add_resource(LoginApi, '/login')
    api.add_resource(LogoutApi, '/logout')
