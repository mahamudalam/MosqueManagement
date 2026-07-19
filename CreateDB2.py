from app import create_app, db

app = create_app()

with app.app_context():
    #print(db.Model.metadata.tables.keys())
    db.create_all()
    print("Database created successfully")