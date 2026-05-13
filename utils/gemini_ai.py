from google import genai
from google.genai import types
import os
import streamlit as st
from dotenv import load_dotenv

# 1. Load local .env file
load_dotenv()

# 2. Retrieve the API Key
api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")

# 3. Initialize the Gemini Client
client = genai.Client(api_key=api_key)

def get_soul_rebel_consultant(user_input, context=""):
    system_instruction = """
    You are the 'Soul Rebel' Strategic Consultant, powered by the Godzspeed Methodology. 
    You do not build institutions; you unearth Individuals.
    
    CORE FRAMEWORK (The Anatomy of the Brand):
    1. SOUL (PurpUS): The nucleus and central nervous system.
    2. MIND (Identity & Strategy): Where passion meets clarity.
    3. BODY (Experience & Impact): The physical expression and legacy.
    
    THE 4 CHAMBERS:
    - CHAMBER 1: PurpUS (The Soul)
    - CHAMBER 2: Brand Identity (The Mind)
    - CHAMBER 3: Brand Experience (The Body)
    - CHAMBER 4: Brand Impact (The Legacy)

    CONSULTING STYLE:
    - Humanize the branding process. 
    - BE PROACTIVE: Always conclude with a deep-diving question.
    - If Chamber 1 is clear, move toward Chamber 2.
    """

    # --- MULTIMODAL HANDSHAKE ---
    # We build a list of "Parts" for Gemini to process
    content_parts = [
        types.Part.from_text(text=f"{system_instruction}\n\n--- CONVERSATION HISTORY ---\n{context}\n\n--- NEW USER INPUT ---")
    ]

    # Check if user_input is a Streamlit UploadedFile (Audio) or a String
    if hasattr(user_input, "read"):
        # Reset file pointer to beginning and read bytes
        user_input.seek(0)
        audio_bytes = user_input.read()
        
        # Add the audio part
        content_parts.append(
            types.Part.from_bytes(
                data=audio_bytes,
                mime_type="audio/wav" # Streamlit audio_input records as wav
            )
        )
    else:
        # Add the text part
        content_parts.append(types.Part.from_text(text=str(user_input)))

    # Generate response 
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=content_parts
        )
        return response.text
    except Exception as e:
        return f"I encountered a soul-searching error: {str(e)}"