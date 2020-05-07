from app import db
import app.models

app = app.create_app()

with app.app_context():
    db.create_all()

print("DB created.")