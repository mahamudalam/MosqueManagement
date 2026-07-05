from app import create_app, db
from app.models import Admin

app = create_app()

with app.app_context():

    admin = Admin.query.filter_by(username="admin").first()

    if not admin:

        admin = Admin(username="admin")

        admin.set_password("admin123")

        db.session.add(admin)

        db.session.commit()

        print("Admin Created")

    else:

        print("Admin Already Exists")