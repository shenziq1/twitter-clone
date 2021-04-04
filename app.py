from flask import Flask, request, jsonify, render_template, flash, redirect, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, current_user, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from flask_restful import Resource, Api


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///twitter_clone.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "LeapGrad"

db = SQLAlchemy(app)
db.init_app(app)

@app.before_first_request
def create_table():
    db.create_all()

login = LoginManager(app)
login.init_app(app)
login.login_view = 'login'

class User(db.Model, UserMixin):
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

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

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


api = Api(app)
initialize_routes(api)

if __name__ == "__main__":
    app.run(debug=True)
