from flask import Flask
from flask_login import LoginManager
from app.models import db, Admin
from config import Config
import os

app = Flask(__name__)

app.config.from_object(Config)

db.init_app(app)

# -------------------------------
# Flask Login
# -------------------------------
login_manager = LoginManager()

login_manager.login_view = "auth.login"

login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))


# -------------------------------
# Create instance folder
# -------------------------------
if not os.path.exists("instance"):
    os.mkdir("instance")


# -------------------------------
# Create database tables
# -------------------------------
with app.app_context():

    db.create_all()

    if Admin.query.filter_by(username="admin").first() is None:
        admin = Admin(
            fullname="System Administrator",
            username="admin",
            role="Admin",
            status="Active"
        )
        admin.set_password("admin123")
        db.session.add(admin)
        db.session.commit()


# -------------------------------
# Import Routes
# -------------------------------
from app.routes import register_routes

register_routes(app)

if __name__ == "__main__":
    app.run(debug=True)