#!/usr/bin/env python3
"""
Simple script to run the Streamlit app
"""

import subprocess
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import streamlit
        import requests
        print("✅ Streamlit and requests are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install dependencies with: pip install -r requirements.txt")
        return False

def check_env_file():
    """Check if .env file exists"""
    if not os.path.exists(".env"):
        print("⚠️  .env file not found")
        print("Creating .env file template...")
        
        with open(".env", "w") as f:
            f.write("OPENAI_API_KEY=your_openai_api_key_here\n")
            f.write("DATABASE_URL=sqlite:///./hospital.db\n")
        
        print("✅ Created .env file template")
        print("Please edit .env file and add your OpenAI API key")
        return False
    
    print("✅ Environment configuration found")
    return True

def main():
    """Main function to run Streamlit"""
    print("🏥 Hospital Appointment Booking System - Streamlit UI")
    print("=" * 50)
    
    # Check dependencies
    print("1. Checking dependencies...")
    if not check_dependencies():
        return False
    
    # Check environment
    print("\n2. Checking environment...")
    if not check_env_file():
        return False
    
    print("\n3. Starting Streamlit app...")
    print("🌐 The app will be available at: http://localhost:8501")
    print("\n⚠️  Make sure the FastAPI server is running on http://localhost:8000")
    print("   Start it with: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
    print("\nPress Ctrl+C to stop the app")
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "streamlit_app.py"
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start Streamlit: {e}")
        return False
    except KeyboardInterrupt:
        print("\n🛑 Streamlit app stopped")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Startup interrupted by user")
        sys.exit(1)
