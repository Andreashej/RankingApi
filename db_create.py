from icerankingapi import db, create_app
import icerankingapi.models

app = create_app()

with app.app_context():
    db.create_all()

print("DB created.")