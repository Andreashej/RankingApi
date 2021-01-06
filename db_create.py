from .app import db, create_app, models

app = create_app()

with app.app_context():
    db.create_all()

print("DB created.")