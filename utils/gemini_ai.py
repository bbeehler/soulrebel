from google import genai
import os
import streamlit as st
from dotenv import load_dotenv

# 1. Load local .env file (used when running on your Mac)
load_dotenv()

# 2. Retrieve the API Key
# This looks in your local environment first, then checks Streamlit Cloud Secrets
api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")

# 3. Initialize the Gemini Client
# We pass the api_key explicitly to ensure the Cloud server sees it
client = genai.Client(api_key=api_key)

def get_soul_rebel_consultant(user_input, context=""):
    system_instruction = """
    You are the 'Soul Rebel' Strategic Consultant. You specialize in the Godzspeed 
    Methodology: PurpUS, Brand Identity, Brand Experience, and Brand Impact.
    Your goal is to help businesses move beyond superficial aesthetics into 
    deep, legacy-building narratives. Be direct, insightful, and visionary.
    """
    
    # Combine instructions, historical context, and new input
    prompt = f"{system_instruction}\n\nContext: {context}\n\nInput: {user_input}"
    
    # Generate response using Gemini 1.5 Pro
    response = client.models.generate_content(
        model="gemini-2.5-pro",
        contents=prompt
    )
    
    return response.text