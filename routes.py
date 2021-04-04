from flask import Flask, request, jsonify, render_template, redirect, make_response
from flask_login import LoginManager, UserMixin, current_user, login_user, logout_user, login_required
from flask_restful import Resource
from models import User

class IndexApi(Resource):
    def get(self):
        if current_user.is_authenticated:
            return "Hello, " + current_user.get_username() + " !"
        else:
            return "Hello, please register or login!"

class UsersApi(Resource):
    def get(self):
        users = User.query.all()
        return jsonify([{"username": i.username, "password_hash": i.password_hash, "id": i.id} for i in users])

class RegisterApi(Resource):

    def get(self):
        if current_user.is_authenticated:
            return redirect('/')
        headers = {'Content-Type': 'text/html'}
        return make_response(render_template('register.html'), 200, headers)

    def post(self):
        try:
            username = request.form['username']
            password = request.form['password']
            password2 = request.form['password2']

            if not (username and password and password2):
                return('Fields required.')

            else:
                if password != password2:
                    return('Password mismatch!')

                if User.query.filter_by(username=username).first():
                    return('User exists, try another username!')

                user = User(username=username, password=password)
                db.session.add(user)
                db.session.commit()
                return redirect('/login')
        except Exception as e:
            return jsonify({"error": e})


class LoginApi(Resource):
    def get(self):
        if current_user.is_authenticated:
            return redirect('/')
        headers = {'Content-Type': 'text/html'}
        return make_response(render_template('login.html'), 200, headers)

    def post(self):
        username = request.form['username']
        user = User.query.filter_by(username = username).first()
        if user is not None and user.check_password(request.form['password']):
            login_user(user)
            return redirect('/')

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
