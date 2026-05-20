from app.core.config import get_settings
from app.core.security import get_password_hash
from app.db.session import Base, SessionLocal, engine
from app.models.user import User

settings = get_settings()

SAMPLE_MEMBERS = [
    ("Aarav Sharma", "aarav@coop.local", "9800000001"),
    ("Sita Thapa", "sita@coop.local", "9800000002"),
    ("Bikash Gurung", "bikash@coop.local", "9800000003"),
    ("Nisha Rai", "nisha@coop.local", "9800000004"),
    ("Ramesh Karki", "ramesh@coop.local", "9800000005"),
    ("Mina Lama", "mina@coop.local", "9800000006"),
    ("Prakash KC", "prakash@coop.local", "9800000007"),
    ("Anita Magar", "anita@coop.local", "9800000008"),
]


def upsert_user(db, name: str, email: str, password: str, role: str, phone: str | None = None):
    user = db.query(User).filter(User.email == email).first()
    if user:
        return user
    user = User(
        name=name,
        email=email,
        phone=phone,
        role=role,
        password_hash=get_password_hash(password),
        is_active=True,
    )
    db.add(user)
    return user


def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        upsert_user(db, "COOP Admin", settings.admin_email, settings.admin_password, "admin")
        for name, email, phone in SAMPLE_MEMBERS:
            upsert_user(db, name, email, "member12345", "member", phone)
        db.commit()
        print("Seed complete")
        print(f"Admin: {settings.admin_email} / {settings.admin_password}")
        print("Member password: member12345")
    finally:
        db.close()


if __name__ == "__main__":
    main()
