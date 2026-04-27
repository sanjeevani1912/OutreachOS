import os
from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv()

def get_api_key(name):
    # Try environment variable first (local/deployment)
    val = os.getenv(name)
    if val: return val
    
    # Try streamlit secrets (deployment)
    try:
        import streamlit as st
        if name in st.secrets:
            return st.secrets[name]
    except:
        pass
    return None

# API Keys
YOUTUBE_API_KEY = get_api_key("YOUTUBE_API_KEY")
GEMINI_API_KEY = get_api_key("GEMINI_API_KEY")

# Filtering Constraints
MIN_FOLLOWERS = 5000
MAX_FOLLOWERS = 100000
TARGET_REGION = "India"

# Brand Context (Example: Education)
BRAND_CONTEXT = {
    "category": "Education",
    "name": "SPARK Olympiads",
    "description": "An online assessment platform for competitive school exams.",
    "target_audience": "Students preparing for math and science olympiads",
    "value_prop": "High-quality practice tests and performance analytics"
}

# Outreach Config
EMAIL_LENGTH_WORDS = (60, 90)
DM_LENGTH_WORDS = (15, 30)
