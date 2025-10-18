from pydantic import BaseModel
from typing import List, Optional


class DoctorOut(BaseModel):
    id: int
    doctor_name: str
    department: str
    available_start: str
    available_end: str
    off_day: Optional[str]

    class Config:
        orm_mode = True


class DoctorIn(BaseModel):
    doctor_name: str
    department: str
    available_start: str
    available_end: str
    off_day: Optional[str] = None


class BookingIn(BaseModel):
    patient_name: str
    doctor_name: str
    date: str  # YYYY-MM-DD
    time_slot: str


class BookingOut(BookingIn):
    id: int

    class Config:
        orm_mode = True


class ChatMessage(BaseModel):
    message: str
    session_id: str


class ChatResponse(BaseModel):
    reply: str
    done: bool
    booking_details: Optional[dict] = None