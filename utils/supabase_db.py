import os
import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv

# Load local .env for your Mac
load_dotenv()

# Get credentials from environment or Streamlit Secrets
url = os.getenv("SUPABASE_URL") or st.secrets.get("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY") or st.secrets.get("SUPABASE_KEY")

# Initialize the Supabase Client
if url and key:
    supabase: Client = create_client(url, key)
else:
    supabase = None

def save_brand_data(user_id, purpus_text):
    """Saves or updates the PurpUS summary in the database."""
    if not supabase:
        return None
    
    data = {
        "user_id": user_id,
        "purpus_summary": purpus_text
    }
    # upsert handles "update if exists, else insert"
    return supabase.table("brand_strategy").upsert(data, on_conflict="user_id").execute()

def load_brand_data(user_id):
    """Retrieves saved brand data for a specific user."""
    if not supabase:
        return None
        
    result = supabase.table("brand_strategy").select("*").eq("user_id", user_id).execute()
    return result.data[0] if result.data else None