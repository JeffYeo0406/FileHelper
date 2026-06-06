"""Create database tables and a default admin account."""
from database import init_db, SessionLocal
from models.user import User
from routers.auth import hash_password


def seed():
    init_db()
    db = SessionLocal()

    existing = db.query(User).filter(User.username == "admin").first()
    if not existing:
        admin = User(
            username="admin",
            email="admin@filehelper.local",
            password_hash=hash_password("changeme123"),
            role="admin"
        )
        db.add(admin)
        db.commit()
        print("✓ Default admin created: admin / changeme123")
    else:
        print("✓ Admin user already exists")

    db.close()
    print("✓ Database ready")


if __name__ == "__main__":
    seed()
