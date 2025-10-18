from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import uvicorn

from .database import get_db, init_db
from .models import Doctor, Booking
from .schemas import (
    DoctorOut, DoctorIn, BookingIn, BookingOut, 
    ChatMessage, ChatResponse
)
from .tools import (
    list_departments, find_doctors_by_department, 
    get_doctor_available_slots, create_booking,
    get_all_doctors, get_patient_bookings
)
from .simple_agent import process_message

# Initialize FastAPI app
app = FastAPI(
    title="Hospital Appointment Booking System",
    description="AI-powered appointment booking system with conversational interface",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()


# Health check endpoint
@app.get("/")
async def root():
    return {"message": "Hospital Appointment Booking System API", "status": "running"}


# Chat endpoint
@app.post("/chat", response_model=ChatResponse)
async def chat(message: ChatMessage):
    """Process chat messages with the AI agent"""
    try:
        result = process_message(message.session_id, message.message)
        return ChatResponse(
            reply=result["reply"],
            done=result["done"],
            booking_details=result["booking_details"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")


# Doctor endpoints
@app.get("/doctors", response_model=List[DoctorOut])
async def get_doctors(db: Session = Depends(get_db)):
    """Get all doctors"""
    doctors = get_all_doctors()
    return doctors


@app.get("/doctors/departments", response_model=List[str])
async def get_departments():
    """Get all available departments"""
    return list_departments()


@app.get("/doctors/department/{department}", response_model=List[DoctorOut])
async def get_doctors_by_department(department: str):
    """Get doctors by department"""
    doctors = find_doctors_by_department(department)
    if not doctors:
        raise HTTPException(status_code=404, detail=f"No doctors found in {department} department")
    return doctors


@app.get("/doctors/{doctor_name}/availability/{date}")
async def get_doctor_availability(doctor_name: str, date: str):
    """Get available time slots for a doctor on a specific date"""
    try:
        slots = get_doctor_available_slots(doctor_name, date)
        return {
            "doctor_name": doctor_name,
            "date": date,
            "available_slots": slots
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting availability: {str(e)}")


# Booking endpoints
@app.post("/bookings", response_model=BookingOut)
async def create_new_booking(booking: BookingIn):
    """Create a new booking"""
    try:
        new_booking = create_booking(
            booking.patient_name,
            booking.doctor_name,
            booking.date,
            booking.time_slot
        )
        if not new_booking:
            raise HTTPException(status_code=400, detail="Time slot is not available")
        return new_booking
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating booking: {str(e)}")


@app.get("/bookings/patient/{patient_name}", response_model=List[BookingOut])
async def get_patient_booking_history(patient_name: str):
    """Get booking history for a patient"""
    bookings = get_patient_bookings(patient_name)
    return bookings


@app.get("/bookings", response_model=List[BookingOut])
async def get_all_bookings(db: Session = Depends(get_db)):
    """Get all bookings (admin endpoint)"""
    bookings = db.query(Booking).all()
    return bookings


# Admin endpoints
@app.post("/doctors", response_model=DoctorOut)
async def add_doctor(doctor: DoctorIn, db: Session = Depends(get_db)):
    """Add a new doctor (admin endpoint)"""
    db_doctor = Doctor(
        doctor_name=doctor.doctor_name,
        department=doctor.department,
        available_start=doctor.available_start,
        available_end=doctor.available_end,
        off_day=doctor.off_day
    )
    db.add(db_doctor)
    db.commit()
    db.refresh(db_doctor)
    return db_doctor


@app.delete("/doctors/{doctor_id}")
async def delete_doctor(doctor_id: int, db: Session = Depends(get_db)):
    """Delete a doctor (admin endpoint)"""
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    db.delete(doctor)
    db.commit()
    return {"message": "Doctor deleted successfully"}


@app.delete("/bookings/{booking_id}")
async def cancel_booking(booking_id: int, db: Session = Depends(get_db)):
    """Cancel a booking"""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    db.delete(booking)
    db.commit()
    return {"message": "Booking cancelled successfully"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
