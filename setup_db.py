from app import app, db
from models import User

with app.app_context():
    db.create_all()
    if not User.query.filter_by(username="admin").first():
        admin = User(username="admin", email="admin@example.com", role="admin")
        admin.set_password("adminpass")
        db.session.add(admin)
        db.session.commit()
    print("DB setup complete! Tables created and admin seeded.")
