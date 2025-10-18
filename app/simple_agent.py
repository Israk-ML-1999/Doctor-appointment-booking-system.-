import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from .tools import (
    list_departments, find_doctors_by_department, find_doctor_by_name,
    get_doctor_available_slots, create_booking, suggest_alternative_slots,
    check_doctor_availability
)


# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Initialize OpenAI
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0.1,
    api_key=os.getenv("OPENAI_API_KEY")
)


class ConversationState:
    def __init__(self):
        self.patient_name = None
        self.intent = None
        self.selected_department = None
        self.selected_doctor = None
        self.selected_date = None
        self.selected_time = None
        self.booking_confirmed = False
        self.booking_details = None
        self.step = "welcome"  # Track current step


# Global conversation states
CONVERSATION_STATES: Dict[str, ConversationState] = {}


def extract_intent_and_entities(message: str) -> Dict:
    """Extract intent and entities from user message using OpenAI"""
    prompt = f"""
    Analyze this message and extract:
    1. Intent: "greeting", "book_appointment", "provide_name", "select_department", "select_doctor", "select_time", "confirm_booking", "other"
    2. Patient name (if mentioned)
    3. Department (if mentioned) - look for: Cardiology, Dermatology, Emergency Medicine, Family Medicine, Gastroenterology, Nephrology, Neurology, Oncology, Ophthalmology, Orthopedics, Pathology, Pediatrics, Radiology, Surgery
    4. Doctor name (if mentioned)
    5. Date (if mentioned, format as YYYY-MM-DD)
    6. Time (if mentioned, format as HH:MM)
    7. Problem description (if mentioned)
    
    Important: If the user mentions a department name (like "pathology", "surgery", "neurology"), set the department field to the full department name.
    
    Message: "{message}"
    
    Return JSON format:
    {{
        "intent": "...",
        "patient_name": "...",
        "department": "...",
        "doctor_name": "...",
        "date": "...",
        "time": "...",
        "problem_description": "..."
    }}
    """
    
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        result = json.loads(response.content)
        
        # Fallback: check for department names directly in the message
        message_lower = message.lower()
        department_mapping = {
            "cardiology": "Cardiology",
            "dermatology": "Dermatology", 
            "emergency medicine": "Emergency Medicine",
            "family medicine": "Family Medicine",
            "gastroenterology": "Gastroenterology",
            "nephrology": "Nephrology",
            "neurology": "Neurology",
            "oncology": "Oncology",
            "ophthalmology": "Ophthalmology",
            "orthopedics": "Orthopedics",
            "pathology": "Pathology",
            "pediatrics": "Pediatrics",
            "radiology": "Radiology",
            "surgery": "Surgery"
        }
        
        for dept_key, dept_name in department_mapping.items():
            if dept_key in message_lower and not result.get("department"):
                result["department"] = dept_name
                result["intent"] = "select_department"
                break
        
        return result
    except Exception as e:
        print(f"Error parsing message: {e}")
        return {"intent": "other"}


def process_message(session_id: str, message: str) -> Dict:
    """Process a user message and return response using simple state machine"""
    
    # Get or create conversation state
    if session_id not in CONVERSATION_STATES:
        CONVERSATION_STATES[session_id] = ConversationState()
    
    state = CONVERSATION_STATES[session_id]
    parsed = extract_intent_and_entities(message)
    
    try:
        # Check if user wants to start over
        if message.lower() in ["hi", "hello", "start over", "reset", "new appointment"]:
            # Reset the conversation state
            state.patient_name = None
            state.intent = None
            state.selected_department = None
            state.selected_doctor = None
            state.selected_date = None
            state.selected_time = None
            state.booking_confirmed = False
            state.booking_details = None
            state.step = "welcome"
            response = "Welcome to our Hospital Appointment Booking System! 🏥\n\nI'm here to help you book an appointment with our doctors. To get started, may I have your full name please?"
        
        # Step 1: Welcome and collect name
        elif state.step == "welcome":
            if not state.patient_name:
                patient_name = parsed.get("patient_name")
                if patient_name:
                    state.patient_name = patient_name
                    state.step = "booking_request"
                    response = f"Nice to meet you, {patient_name}! 👋\n\nHow can I help you today? Would you like to book an appointment with one of our doctors?"
                else:
                    response = "Welcome to our Hospital Appointment Booking System! 🏥\n\nI'm here to help you book an appointment with our doctors. To get started, may I have your full name please?"
            else:
                state.step = "booking_request"
                response = f"Hello {state.patient_name}! How can I help you today? Would you like to book an appointment?"
        
        # Step 2: Handle booking request
        elif state.step == "booking_request":
            intent = parsed.get("intent")
            if intent == "book_appointment" or "book" in message.lower() or "appointment" in message.lower():
                departments = list_departments()
                dept_list = "\n".join([f"• {dept}" for dept in departments])
                response = f"Great! I'd be happy to help you book an appointment. 🩺\n\nWhat type of doctor would you like to see? You can either:\n\n1. Tell me which department you need:\n{dept_list}\n\n2. Describe your problem/symptoms and I'll suggest the right department for you.\n\nWhat would you prefer?"
                state.step = "department_selection"
            else:
                response = "I'm here to help you book an appointment. Would you like to book an appointment with one of our doctors?"
        
        # Step 3: Handle department selection
        elif state.step == "department_selection":
            department = parsed.get("department")
            problem = parsed.get("problem_description")
            
            # If no department mentioned, try to infer from problem description
            if not department and problem:
                problem_lower = problem.lower()
                if any(word in problem_lower for word in ["heart", "chest", "cardiac"]):
                    department = "Cardiology"
                elif any(word in problem_lower for word in ["skin", "rash", "dermatitis"]):
                    department = "Dermatology"
                elif any(word in problem_lower for word in ["child", "baby", "pediatric"]):
                    department = "Pediatrics"
                elif any(word in problem_lower for word in ["bone", "joint", "fracture"]):
                    department = "Orthopedics"
                elif any(word in problem_lower for word in ["eye", "vision", "sight"]):
                    department = "Ophthalmology"
                elif any(word in problem_lower for word in ["brain", "headache", "neurological"]):
                    department = "Neurology"
                elif any(word in problem_lower for word in ["stomach", "digestive", "gastro"]):
                    department = "Gastroenterology"
                elif any(word in problem_lower for word in ["kidney", "renal", "urinary"]):
                    department = "Nephrology"
                elif any(word in problem_lower for word in ["cancer", "tumor", "oncology"]):
                    department = "Oncology"
                elif any(word in problem_lower for word in ["surgery", "operation", "surgical"]):
                    department = "Surgery"
                elif any(word in problem_lower for word in ["family", "general", "primary"]):
                    department = "Family Medicine"
                elif any(word in problem_lower for word in ["emergency", "urgent", "acute"]):
                    department = "Emergency Medicine"
                elif any(word in problem_lower for word in ["x-ray", "scan", "imaging"]):
                    department = "Radiology"
                elif any(word in problem_lower for word in ["test", "lab", "pathology"]):
                    department = "Pathology"
            
            if department:
                doctors = find_doctors_by_department(department)
                if doctors:
                    doctor_list = "\n".join([f"• {doc.doctor_name}" for doc in doctors])
                    response = f"Perfect! I found these doctors in the {department} department:\n\n{doctor_list}\n\nWhich doctor would you like to book an appointment with?"
                    state.selected_department = department
                    state.step = "doctor_selection"
                else:
                    departments = list_departments()
                    dept_list = "\n".join([f"• {dept}" for dept in departments])
                    response = f"I couldn't find any doctors in the {department} department. Here are the available departments:\n\n{dept_list}\n\nPlease choose from the list above."
            else:
                response = "I need a bit more information. Could you please tell me which department you need or describe your problem so I can suggest the right doctor for you?"
        
        # Step 4: Handle doctor selection
        elif state.step == "doctor_selection":
            doctor_name = parsed.get("doctor_name")
            department = parsed.get("department")
            
            # Check if user wants to change department
            if department and department.lower() != state.selected_department.lower():
                # User wants to change department
                doctors = find_doctors_by_department(department)
                if doctors:
                    doctor_list = "\n".join([f"• {doc.doctor_name}" for doc in doctors])
                    response = f"Perfect! I found these doctors in the {department} department:\n\n{doctor_list}\n\nWhich doctor would you like to book an appointment with?"
                    state.selected_department = department
                    state.step = "doctor_selection"
                else:
                    departments = list_departments()
                    dept_list = "\n".join([f"• {dept}" for dept in departments])
                    response = f"I couldn't find any doctors in the {department} department. Here are the available departments:\n\n{dept_list}\n\nPlease choose from the list above."
                    state.step = "department_selection"
            elif doctor_name:
                doctor = find_doctor_by_name(doctor_name)
                if doctor:
                    today = datetime.now().strftime("%Y-%m-%d")
                    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
                    response = f"Excellent choice! {doctor.doctor_name} is a great {doctor.department} specialist. 🩺\n\nWhat date would you like to book your appointment? You can say:\n• Today ({today})\n• Tomorrow ({tomorrow})\n• Or any specific date (YYYY-MM-DD format)\n\nPlease note: {doctor.doctor_name} is off on {doctor.off_day}s."
                    state.selected_doctor = doctor.doctor_name
                    state.step = "date_selection"
                else:
                    response = f"I couldn't find a doctor named {doctor_name}. Could you please check the spelling and try again?"
            else:
                # Check if user mentioned a department name directly
                message_lower = message.lower()
                if any(dept.lower() in message_lower for dept in ["cardiology", "dermatology", "emergency medicine", "family medicine", 
                                                                "gastroenterology", "nephrology", "neurology", "oncology", 
                                                                "ophthalmology", "orthopedics", "pathology", "pediatrics", 
                                                                "radiology", "surgery"]):
                    # Extract department from message
                    for dept in ["Cardiology", "Dermatology", "Emergency Medicine", "Family Medicine", 
                                "Gastroenterology", "Nephrology", "Neurology", "Oncology", 
                                "Ophthalmology", "Orthopedics", "Pathology", "Pediatrics", 
                                "Radiology", "Surgery"]:
                        if dept.lower() in message_lower:
                            doctors = find_doctors_by_department(dept)
                            if doctors:
                                doctor_list = "\n".join([f"• {doc.doctor_name}" for doc in doctors])
                                response = f"Perfect! I found these doctors in the {dept} department:\n\n{doctor_list}\n\nWhich doctor would you like to book an appointment with?"
                                state.selected_department = dept
                                state.step = "doctor_selection"
                                break
                            else:
                                response = f"I couldn't find any doctors in the {dept} department. Please choose a different department."
                                state.step = "department_selection"
                                break
                else:
                    response = "I didn't catch the doctor's name. Could you please tell me which doctor you'd like to book an appointment with, or if you want to change departments, just tell me the department name."
        
        # Step 5: Handle date selection
        elif state.step == "date_selection":
            date = parsed.get("date")
            
            # Handle common date expressions
            if not date:
                if "today" in message.lower():
                    date = datetime.now().strftime("%Y-%m-%d")
                elif "tomorrow" in message.lower():
                    date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
            
            if date:
                # Check if doctor is available on this date
                if not check_doctor_availability(state.selected_doctor, date):
                    doctor = find_doctor_by_name(state.selected_doctor)
                    response = f"Sorry, {state.selected_doctor} is not available on {date} (it's their {doctor.off_day} off day). Please choose a different date."
                else:
                    # Get available time slots
                    available_slots = get_doctor_available_slots(state.selected_doctor, date)
                    
                    if available_slots:
                        slots_text = "\n".join([f"• {slot}" for slot in available_slots[:10]])  # Show first 10 slots
                        response = f"Great! Here are the available time slots for {state.selected_doctor} on {date}:\n\n{slots_text}\n\nWhich time slot would you prefer? (Each appointment is 20 minutes long)"
                        state.selected_date = date
                        state.step = "time_selection"
                    else:
                        response = f"Sorry, {state.selected_doctor} has no available slots on {date}. Please choose a different date."
            else:
                response = "I need a specific date for your appointment. Please tell me which date you'd like (today, tomorrow, or a specific date in YYYY-MM-DD format)."
        
        # Step 6: Handle time selection
        elif state.step == "time_selection":
            time = parsed.get("time")
            
            if time:
                # Check if the time slot is still available
                available_slots = get_doctor_available_slots(state.selected_doctor, state.selected_date)
                
                if time in available_slots:
                    # Confirm booking details
                    response = f"Perfect! Let me confirm your appointment details:\n\n👤 Patient: {state.patient_name}\n🩺 Doctor: {state.selected_doctor}\n📅 Date: {state.selected_date}\n⏰ Time: {time}\n\nIs this correct? Please say 'yes' to confirm or 'no' to make changes."
                    state.selected_time = time
                    state.step = "confirm_booking"
                else:
                    # Suggest alternative slots
                    alternatives = suggest_alternative_slots(state.selected_doctor, state.selected_date, time)
                    if alternatives:
                        alt_text = "\n".join([f"• {alt}" for alt in alternatives])
                        response = f"Sorry, {time} is no longer available. Here are some alternative time slots:\n\n{alt_text}\n\nWhich one would you prefer?"
                    else:
                        response = f"Sorry, {time} is not available and there are no alternative slots. Please choose a different date."
                        state.step = "date_selection"
            else:
                response = "I need a specific time for your appointment. Please choose from the available time slots I showed you."
        
        # Step 7: Confirm booking
        elif state.step == "confirm_booking":
            if "yes" in message.lower() or "confirm" in message.lower():
                # Create the booking
                booking = create_booking(
                    state.patient_name,
                    state.selected_doctor,
                    state.selected_date,
                    state.selected_time
                )
                
                if booking:
                    response = f"🎉 Congratulations! Your appointment has been successfully booked!\n\n📋 Booking Details:\n• Patient: {state.patient_name}\n• Doctor: {state.selected_doctor}\n• Date: {state.selected_date}\n• Time: {state.selected_time}\n• Duration: 20 minutes\n\nPlease arrive 10 minutes before your appointment time. If you need to cancel or reschedule, please contact us at least 24 hours in advance.\n\nIs there anything else I can help you with?"
                    state.booking_confirmed = True
                    state.booking_details = {
                        "id": booking.id,
                        "patient_name": booking.patient_name,
                        "doctor_name": booking.doctor_name,
                        "date": booking.date,
                        "time_slot": booking.time_slot
                    }
                    state.step = "completed"
                else:
                    response = "Sorry, there was an error creating your booking. The time slot may have been taken by someone else. Please try again with a different time slot."
                    state.step = "time_selection"
            else:
                response = "No problem! What would you like to change? You can modify the doctor, date, or time."
        
        # Step 8: Completed
        elif state.step == "completed":
            response = "Your appointment has been successfully booked! Is there anything else I can help you with?"
        
        else:
            response = "I'm sorry, I didn't understand that. Could you please try again?"
        
        return {
            "reply": response,
            "done": state.booking_confirmed,
            "booking_details": state.booking_details
        }
    
    except Exception as e:
        print(f"Error processing message: {e}")
        return {
            "reply": "I'm sorry, there was an error processing your request. Please try again.",
            "done": False,
            "booking_details": None
        }
