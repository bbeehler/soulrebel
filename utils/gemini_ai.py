from google import genai
import os
from dotenv import load_dotenv

# Load your secret API key from the .env file
load_dotenv()
client = genai.Client()

def get_soul_rebel_consultant(user_input, context=""):
    system_instruction = """
    You are the 'Soul Rebel' Strategic Consultant. You specialize in the Godzspeed 
    Methodology: PurpUS, Brand Identity, Brand Experience, and Brand Impact.
    Your goal is to help businesses move beyond superficial aesthetics into 
    deep, legacy-building narratives. Be direct, insightful, and visionary.
    """
    
    prompt = f"{system_instruction}\n\nContext: {context}\n\nInput: {user_input}"
    
    # Using Gemini Pro for deep strategy
    response = client.models.generate_content(
        model="gemini-1.5-pro",
        contents=prompt
    )
    
    return response.text