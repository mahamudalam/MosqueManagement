from flask import Flask
from flask_login import LoginManager
from app.models import db,Admin
from config import Config
import os

app=Flask(__name__)

app.config.from_object(Config)

db.init_app(app)

login_manager=LoginManager()

login_manager.login_view="login"

login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):

    return Admin.query.get(int(user_id))

if not os.path.exists("instance"):
    os.mkdir("instance")

with app.app_context():

    db.create_all()

    if Admin.query.count()==0:

        admin=Admin(username="admin")

        admin.set_password("admin123")

        db.session.add(admin)

        db.session.commit()

from app.routes import *

if __name__=="__main__":

    app.run(debug=True)