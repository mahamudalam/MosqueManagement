from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy import inspect, text


db = SQLAlchemy()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    from app.models import Admin
    from app.routes import register_routes

    register_routes(app)

    with app.app_context():
        db.create_all()

        inspector = inspect(db.engine)
        if "admin" in inspector.get_table_names():
            columns = {column["name"] for column in inspector.get_columns("admin")}
            if "password" in columns:
                db.session.execute(text("""
                    CREATE TABLE admin_new (
                        id INTEGER NOT NULL,
                        fullname VARCHAR(100) NOT NULL,
                        username VARCHAR(50) NOT NULL,
                        password_hash VARCHAR(255),
                        role VARCHAR(30),
                        status VARCHAR(20),
                        created_date DATETIME,
                        PRIMARY KEY (id),
                        UNIQUE (username)
                    )
                """))
                db.session.execute(text("""
                    INSERT INTO admin_new (id, fullname, username, password_hash, role, status, created_date)
                    SELECT id, fullname, username, password_hash, role, status, created_date
                    FROM admin
                """))
                db.session.execute(text("DROP TABLE admin"))
                db.session.execute(text("ALTER TABLE admin_new RENAME TO admin"))
                db.session.commit()
                columns = {column["name"] for column in inspector.get_columns("admin")}
            if "fullname" not in columns:
                db.session.execute(text("ALTER TABLE admin ADD COLUMN fullname VARCHAR(100) DEFAULT 'System Administrator'"))
            if "created_date" not in columns:
                db.session.execute(text("ALTER TABLE admin ADD COLUMN created_date DATETIME"))
            if "role" not in columns:
                db.session.execute(text("ALTER TABLE admin ADD COLUMN role VARCHAR(30) DEFAULT 'Committee Member'"))
            if "status" not in columns:
                db.session.execute(text("ALTER TABLE admin ADD COLUMN status VARCHAR(20) DEFAULT 'Active'"))
            if "password_hash" not in columns:
                db.session.execute(text("ALTER TABLE admin ADD COLUMN password_hash VARCHAR(255)"))
            db.session.commit()

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

    return app