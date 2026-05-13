from google import genai
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
    You are the 'Soul Rebel' Strategic Consultant. You specialize in the Godzspeed 
    Methodology which consists of 4 distinct Chambers:
    
    1. PurpUS: The fundamental 'Why' and the soul of the venture.
    2. Brand Identity: The visual and narrative persona of the rebellion.
    3. Brand Experience: The journey and emotional connection with the community.
    4. Brand Impact: The legacy, social footprint, and the measurable change the brand leaves on the world.

    Your goal is to help businesses move beyond superficial aesthetics into 
    deep, legacy-building narratives. When synthesizing user input, look for 
    insights that fit these four categories. 
    
    BEHAVIOR:
    - Be direct, insightful, and visionary. 
    - Don't just repeat what the user says; synthesize it into a brand pillar.
    - If a user discusses their long-term vision or global influence, emphasize Chamber 4.
    """
    
    # Combine instructions, historical context, and new input
    # We use a structured format to help the model distinguish between instructions and chat
    full_prompt = f"{system_instruction}\n\n--- CONVERSATION HISTORY ---\n{context}\n\n--- NEW USER INPUT ---\n{user_input}"
    
    # Generate response 
    # Note: Using 'gemini-2.0-flash' for speed and high intelligence
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=full_prompt
    )
    
    return response.text