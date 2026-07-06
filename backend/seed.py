import datetime
from sqlalchemy.orm import Session
from database import engine, SessionLocal, Base
import models, auth

def seed_database():
    print("Creating database schema...")
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    try:
        # Check if users exist
        if db.query(models.User).first():
            print("Database already contains users. Skipping seed.")
            return

        print("Seeding Users...")
        admin_user = models.User(
            email="admin@enterprise.local",
            hashed_password=auth.get_password_hash("AdminSecret123!"),
            role=models.UserRole.admin,
            is_active=True
        )
        estimator_user = models.User(
            email="estimator@enterprise.local",
            hashed_password=auth.get_password_hash("EstSecret123!"),
            role=models.UserRole.estimator,
            is_active=True
        )
        db.add_all([admin_user, estimator_user])
        db.commit()

        print("Database initialized successfully with default user accounts!")
        print("----------------------------------------------------------------")
        print("Admin Credentials:      admin@enterprise.local / AdminSecret123!")
        print("Estimator Credentials:  estimator@enterprise.local / EstSecret123!")
        print("----------------------------------------------------------------")

    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
