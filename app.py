from flask import Flask
from flask_login import LoginManager
from flask_restful import Api
from db import initialize_db, db
from models import User
from routes import initialize_routes


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///twitter_clone.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "LeapGrad"

initialize_db(app)

@app.before_first_request
def create_table():
    db.create_all()

login = LoginManager(app)
login.init_app(app)
login.login_view = 'login'

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

api = Api(app)
initialize_routes(api)

if __name__ == "__main__":
    app.run(debug=True)
