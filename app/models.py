from sqlalchemy import Column, Integer, String, Date, Time
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Doctor(Base):
    __tablename__ = "doctors"
    id = Column(Integer, primary_key=True, index=True)
    doctor_name = Column(String, index=True)
    department = Column(String, index=True)
    available_start = Column(String)  # e.g., "09:00"
    available_end = Column(String)    # e.g., "17:00"
    off_day = Column(String, nullable=True)  # e.g., "Friday"


class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, index=True)
    patient_name = Column(String, index=True)
    doctor_name = Column(String, index=True)
    date = Column(String)  # YYYY-MM-DD as string for simplicity
    time_slot = Column(String)  # e.g., "09:00", "09:20", etc.