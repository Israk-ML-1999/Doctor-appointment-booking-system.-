import streamlit as st
import requests
import json
import uuid
from datetime import datetime
import time

# Configure Streamlit page
st.set_page_config(
    page_title="Hospital Appointment Booking System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API base URL
API_BASE_URL = "http://localhost:8000"

# Initialize session state
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

if "booking_details" not in st.session_state:
    st.session_state.booking_details = None


def send_message(message: str) -> dict:
    """Send message to the API"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/chat",
            json={
                "message": message,
                "session_id": st.session_state.session_id
            }
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {
            "reply": f"Sorry, I'm having trouble connecting to the server. Error: {str(e)}",
            "done": False,
            "booking_details": None
        }


def get_doctors():
    """Get all doctors from API"""
    try:
        response = requests.get(f"{API_BASE_URL}/doctors")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return []


def get_departments():
    """Get all departments from API"""
    try:
        response = requests.get(f"{API_BASE_URL}/doctors/departments")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return []


def main():
    # Header
    st.title("🏥 Hospital Appointment Booking System")
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.header("🏥 Hospital Info")
        
        # Show departments
        st.subheader("Available Departments")
        departments = get_departments()
        if departments:
            for dept in departments:
                st.write(f"• {dept}")
        else:
            st.write("Loading departments...")
        
        st.markdown("---")
        
        # Reset conversation button
        if st.button("🔄 Start New Conversation"):
            st.session_state.messages = []
            st.session_state.booking_details = None
            st.session_state.session_id = str(uuid.uuid4())
            st.rerun()
    
    # Main chat interface
    st.subheader("💬 Chat with our AI Assistant")
    
    # Display chat messages
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            if message["role"] == "user":
                with st.chat_message("user"):
                    st.write(message["content"])
            else:
                with st.chat_message("assistant"):
                    st.write(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.write(prompt)
        
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = send_message(prompt)
            
            # Display AI response
            st.write(response["reply"])
            
            # Add AI response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response["reply"]})
            
            # Store booking details if available
            if response.get("booking_details"):
                st.session_state.booking_details = response["booking_details"]
    
    # Booking status
    if st.session_state.booking_details:
        st.markdown("---")
        st.success("✅ Appointment Booked!")
        booking = st.session_state.booking_details
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Booking Details:**")
            st.write(f"**Patient:** {booking['patient_name']}")
            st.write(f"**Doctor:** {booking['doctor_name']}")
        with col2:
            st.write(f"**Date:** {booking['date']}")
            st.write(f"**Time:** {booking['time_slot']}")
            st.write(f"**Duration:** 20 minutes")
        
        st.info("💡 Please arrive 10 minutes before your appointment time.")
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: gray;'>
            <p>🏥 Hospital Appointment Booking System | Powered by AI</p>
            <p>Need help? Just ask our AI assistant!</p>
        </div>
        """,
        unsafe_allow_html=True
    )




if __name__ == "__main__":
    # Check if API is running
    try:
        response = requests.get(f"{API_BASE_URL}/")
        if response.status_code == 200:
            main()
        else:
            st.error("❌ API server is not responding. Please make sure the FastAPI server is running on http://localhost:8000")
    except requests.exceptions.RequestException:
        st.error("❌ Cannot connect to API server. Please make sure the FastAPI server is running on http://localhost:8000")
        
        st.markdown("### 🚀 To start the API server:")
        st.code("""
        # Install dependencies
        pip install -r requirements.txt
        
        # Start the FastAPI server
        uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
        """)
        
        st.markdown("### 📝 Don't forget to:")
        st.write("1. Create a `.env` file with your OpenAI API key:")
        st.code("OPENAI_API_KEY=your_openai_api_key_here")
        
        st.write("2. Make sure the `demo_db.json` file is in the project root")
