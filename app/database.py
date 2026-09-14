import os
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash

db = SQLAlchemy()


def init_db(app):
    """Seed the database with the default admin account if it doesn't exist."""
    from .models import User

    admin_password = os.environ.get('ADMIN_PASSWORD')
    if not admin_password:
        raise RuntimeError(
            'ADMIN_PASSWORD tidak ditemukan di environment. '
            'Tambahkan ADMIN_PASSWORD=... ke file .env'
        )

    with app.app_context():
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                password_hash=generate_password_hash(admin_password),
                full_name='Administrator',
                role='admin',
                is_active=True,
            )
            db.session.add(admin)
            db.session.commit()
            print('[init_db] Default admin created  →  username: admin')
