from datetime import datetime, timedelta
from typing import List, Optional
from .database import SessionLocal
from .models import Doctor, Booking


def list_departments() -> List[str]:
    """Get all available departments"""
    db = SessionLocal()
    deps = db.query(Doctor.department).distinct().all()
    db.close()
    return [d[0] for d in deps]


def find_doctors_by_department(dept: str) -> List[Doctor]:
    """Find doctors by department"""
    db = SessionLocal()
    docs = db.query(Doctor).filter(Doctor.department.ilike(f"%{dept}%")).all()
    db.close()
    return docs


def find_doctor_by_name(name: str) -> Optional[Doctor]:
    """Find doctor by name"""
    db = SessionLocal()
    doc = db.query(Doctor).filter(Doctor.doctor_name.ilike(f"%{name}%")).first()
    db.close()
    return doc


def generate_time_slots(start_time: str, end_time: str) -> List[str]:
    """Generate 20-minute time slots between start and end time"""
    slots = []
    start = datetime.strptime(start_time, "%H:%M")
    end = datetime.strptime(end_time, "%H:%M")
    
    current = start
    while current < end:
        slots.append(current.strftime("%H:%M"))
        current += timedelta(minutes=20)
    
    return slots


def get_doctor_available_slots(doctor_name: str, date: str) -> List[str]:
    """Get available time slots for a doctor on a specific date"""
    db = SessionLocal()
    
    # Get doctor info
    doc = db.query(Doctor).filter(Doctor.doctor_name == doctor_name).first()
    if not doc:
        db.close()
        return []
    
    # Generate all possible slots
    all_slots = generate_time_slots(doc.available_start, doc.available_end)
    
    # Get already booked slots
    booked = db.query(Booking).filter(
        Booking.doctor_name == doctor_name, 
        Booking.date == date
    ).all()
    booked_slots = [b.time_slot for b in booked]
    
    db.close()
    
    # Return available slots
    available = [s for s in all_slots if s not in booked_slots]
    return available


def create_booking(patient_name: str, doctor_name: str, date: str, time_slot: str) -> Optional[Booking]:
    """Create a new booking"""
    db = SessionLocal()
    
    # Check if slot is already booked
    exists = db.query(Booking).filter(
        Booking.doctor_name == doctor_name, 
        Booking.date == date, 
        Booking.time_slot == time_slot
    ).first()
    
    if exists:
        db.close()
        return None
    
    # Create booking
    booking = Booking(
        patient_name=patient_name,
        doctor_name=doctor_name,
        date=date,
        time_slot=time_slot
    )
    
    db.add(booking)
    db.commit()
    db.refresh(booking)
    db.close()
    
    return booking


def get_booking_details(booking_id: int) -> Optional[Booking]:
    """Get booking details by ID"""
    db = SessionLocal()
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    db.close()
    return booking


def suggest_alternative_slots(doctor_name: str, date: str, preferred_time: str) -> List[str]:
    """Suggest alternative time slots if preferred time is not available"""
    available_slots = get_doctor_available_slots(doctor_name, date)
    
    if not available_slots:
        return []
    
    # If preferred time is available, return it
    if preferred_time in available_slots:
        return [preferred_time]
    
    # Find closest available slots
    preferred_dt = datetime.strptime(preferred_time, "%H:%M")
    available_dts = [datetime.strptime(slot, "%H:%M") for slot in available_slots]
    
    # Sort by time difference from preferred time
    available_dts.sort(key=lambda x: abs((x - preferred_dt).total_seconds()))
    
    # Return up to 3 closest alternatives
    return [dt.strftime("%H:%M") for dt in available_dts[:3]]


def check_doctor_availability(doctor_name: str, date: str) -> bool:
    """Check if doctor is available on a specific date"""
    db = SessionLocal()
    doc = db.query(Doctor).filter(Doctor.doctor_name == doctor_name).first()
    db.close()
    
    if not doc:
        return False
    
    # Check if it's the doctor's off day
    date_obj = datetime.strptime(date, "%Y-%m-%d")
    day_name = date_obj.strftime("%A")
    
    if doc.off_day and day_name == doc.off_day:
        return False
    
    return True


def get_all_doctors() -> List[Doctor]:
    """Get all doctors"""
    db = SessionLocal()
    doctors = db.query(Doctor).all()
    db.close()
    return doctors


def get_patient_bookings(patient_name: str) -> List[Booking]:
    """Get all bookings for a patient"""
    db = SessionLocal()
    bookings = db.query(Booking).filter(Booking.patient_name == patient_name).all()
    db.close()
    return bookings