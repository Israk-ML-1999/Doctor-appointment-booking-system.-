import json
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base, Doctor, Booking
from dotenv import load_dotenv


load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./hospital.db")


engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db(seed_path: str = "demo_db.json"):
    """Initialize database with seed data"""
    Base.metadata.create_all(bind=engine)
    # load seed if DB empty
    db = SessionLocal()
    dcount = db.query(Doctor).count()
    if dcount == 0:
        with open(seed_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for d in data.get("doctors", []):
            doc = Doctor(
                doctor_name=d["doctor_name"],
                department=d["department"],
                available_start=d["available_start"],
                available_end=d["available_end"],
                off_day=d.get("off_day")
            )
            db.add(doc)
        db.commit()
    db.close()