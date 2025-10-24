# Hospital Doctor Appointment Booking System

An AI-powered appointment booking system with conversational interface built using FastAPI, Langchain, OpenAI, and Streamlit.

## Features

- 🤖 **AI Chat Assistant**: Natural language conversation for booking appointments
- 🏥 **Doctor Management**: Support for multiple departments and doctors
- 📅 **Smart Scheduling**: 20-minute appointment slots with availability checking
- 💬 **Conversational UI**: User-friendly Streamlit interface
- 🔄 **Real-time Updates**: Live availability checking and booking confirmation

## Departments Available

- Cardiology
- Dermatology
- Emergency Medicine
- Family Medicine
- Gastroenterology
- Nephrology
- Neurology
- Oncology
- Ophthalmology
- Orthopedics
- Pathology
- Pediatrics
- Radiology
- Surgery

## Technology Stack

- **Backend**: FastAPI
- **AI/LLM**: OpenAI GPT-3.5-turbo, LangGraph
- **Database**: SQLAlchemy with SQLite
- **Frontend**: Streamlit
- **API Integration**: HTTP requests

## Quick Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Configuration

Create a `.env` file in the project root with your OpenAI API key:

```env
OPENAI_API_KEY=your_openai_api_key_here
DATABASE_URL=sqlite:///./hospital.db
```

### 3. Start the Application

#### Option 1: Windows (Easiest)
Double-click `start.bat` - it will start both servers automatically.

#### Option 2: Manual Start
```bash
# Terminal 1: Start FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Start Streamlit app
streamlit run streamlit_app.py
```

#### Option 3: Python Script
```bash
python run_streamlit.py
```

## Usage

### Chat Interface

1. Open the Streamlit app in your browser (usually `http://localhost:8501`)
2. Start a conversation with the AI assistant
3. Follow the natural conversation flow to book an appointment

### Example Conversation Flow

```
User: Hi, I'd like to book an appointment
AI: Welcome to our Hospital Appointment Booking System! 🏥
    I'm here to help you book an appointment with our doctors. 
    To get started, may I have your full name please?

User: My name is John Smith
AI: Nice to meet you, John Smith! 👋
    How can I help you today? Would you like to book an appointment with one of our doctors?

User: Yes, I need to see a cardiologist
AI: Great! I'd be happy to help you book an appointment. 🩺
    I found these doctors in the Cardiology department:
    • Dr. Ayesha Rahman
    Which doctor would you like to book an appointment with?

User: Dr. Ayesha Rahman
AI: Excellent choice! Dr. Ayesha Rahman is a great Cardiology specialist. 🩺
    What date would you like to book your appointment? You can say:
    • Today (2024-01-15)
    • Tomorrow (2024-01-16)
    • Or any specific date (YYYY-MM-DD format)
    Please note: Dr. Ayesha Rahman is off on Fridays.

User: Tomorrow
AI: Great! Here are the available time slots for Dr. Ayesha Rahman on 2024-01-16:
    • 09:00
    • 09:20
    • 09:40
    • 10:00
    • 10:20
    Which time slot would you prefer? (Each appointment is 20 minutes long)

User: 09:00
AI: Perfect! Let me confirm your appointment details:
    👤 Patient: John Smith
    🩺 Doctor: Dr. Ayesha Rahman
    📅 Date: 2024-01-16
    ⏰ Time: 09:00
    Is this correct? Please say 'yes' to confirm or 'no' to make changes.

User: Yes
AI: 🎉 Congratulations! Your appointment has been successfully booked!
    📋 Booking Details:
    • Patient: John Smith
    • Doctor: Dr. Ayesha Rahman
    • Date: 2024-01-16
    • Time: 09:00
    • Duration: 20 minutes
    Please arrive 10 minutes before your appointment time. 
    If you need to cancel or reschedule, please contact us at least 24 hours in advance.
    Is there anything else I can help you with?
```

## API Endpoints

### Chat
- `POST /chat` - Process chat messages with AI agent

### Doctors
- `GET /doctors` - Get all doctors
- `GET /doctors/departments` - Get all departments
- `GET /doctors/department/{department}` - Get doctors by department
- `GET /doctors/{doctor_name}/availability/{date}` - Get doctor availability

### Bookings
- `POST /bookings` - Create new booking
- `GET /bookings/patient/{patient_name}` - Get patient booking history
- `GET /bookings` - Get all bookings (admin)

## Project Structure

```
appointment_booking_system/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── models.py            # Database models
│   ├── schemas.py           # Pydantic schemas
│   ├── database.py          # Database configuration
│   ├── tools.py             # Utility functions
│   └── simple_agent.py      # AI agent implementation
├── demo_db.json             # Sample doctor data
├── streamlit_app.py         # Streamlit UI
├── run_streamlit.py         # Streamlit startup script
├── start.bat               # Windows batch file
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Key Features

### AI Agent Capabilities
- Natural language understanding
- Intent recognition
- Entity extraction
- Context-aware responses
- Multi-step conversation flow

### Smart Scheduling
- 20-minute appointment slots
- Real-time availability checking
- Doctor off-day handling
- Alternative time suggestions

### User Experience
- Conversational interface
- Real-time chat
- Booking confirmation
- Error handling and recovery

## Troubleshooting

### Common Issues

1. **OpenAI API Key Error**
   - Make sure your `.env` file contains a valid OpenAI API key
   - Check that the API key has sufficient credits

2. **Database Connection Error**
   - Ensure the database file has proper permissions
   - Check that SQLite is properly installed

3. **Port Already in Use**
   - Change the port in the startup command
   - Kill existing processes using the port

### Getting Help

If you encounter any issues:
1. Check the console logs for error messages
2. Verify all dependencies are installed correctly
3. Ensure the `.env` file is properly configured
4. Make sure both FastAPI and Streamlit servers are running

## Contributing

Feel free to contribute to this project by:
- Adding new features
- Improving the AI agent
- Enhancing the UI/UX
- Adding more departments or doctors
- Improving error handling

## License

This project is open source and available under the MIT License.
