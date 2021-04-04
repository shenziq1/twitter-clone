from flask import Flask, request, jsonify, render_template, flash, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, current_user, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from flask_restful import Resource


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

@login_required
@app.route('/')
def index():
    if current_user.is_authenticated:
        return "Hello, " + current_user.get_username() + " !"
    else:
        return "Hello, please register or login!"

@app.route('/users')
def users():
    users = User.query.all()
    return jsonify([{"username": i.username, "password_hash": i.password_hash, "id": i.id} for i in users])

@app.route('/register', methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        return redirect('/')
    if request.method == 'POST':

        try:
            username = request.form['username']
            password = request.form['password']
            password2 = request.form['password2']

            if not (username and password and password2):
                raise InvalidParameter

            else:

                if password != password2:
                    raise Exception('Password mismatch!')

                if User.query.filter_by(username=username).first():
                    raise Exception('User exists, try another username!')

                user = User(username=username, password=password)
                db.session.add(user)
                db.session.commit()
                return redirect('/login')
        except Exception as e:
            return jsonify({"error": e})

    return render_template('register.html')

@app.route('/login', methods = ['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect('/')

    if request.method == 'POST':
        username = request.form['username']
        user = User.query.filter_by(username = username).first()
        if user is not None and user.check_password(request.form['password']):
            login_user(user)
            return redirect('/')

    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)
