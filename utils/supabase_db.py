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

def save_brand_data(user_id, text, chamber="purpus_summary"):
    """
    Saves or updates a specific chamber in the brand_strategy table.
    Targets: 'purpus_summary', 'brand_identity', 'brand_experience', 
    'brand_impact', and now 'soul_guide'.
    """
    if not supabase:
        return None
    
    # We use upsert so that if the user doesn't have a row yet, it creates one.
    # If they do, it only updates the specific chamber provided.
    data = {
        "user_id": user_id,
        chamber: text
    }
    
    try:
        return supabase.table("brand_strategy").upsert(data, on_conflict="user_id").execute()
    except Exception as e:
        st.error(f"Database Save Error: {e}")
        return None

def update_chamber_data(user_id, chamber_column, new_text):
    """
    Surgically updates a specific column for a specific user.
    Used by Profile Settings and the Soul Guide Editor.
    """
    if not supabase:
        return None
        
    data = {chamber_column: new_text}
    try:
        return supabase.table("brand_strategy").update(data).eq("user_id", user_id).execute()
    except Exception as e:
        st.error(f"Database Update Error: {e}")
        return None

def load_brand_data(user_id):
    """
    Retrieves the full brand strategy row (all chambers + soul_guide) 
    for the logged-in user.
    """
    if not supabase:
        return None
        
    try:
        result = supabase.table("brand_strategy").select("*").eq("user_id", user_id).execute()
        # Return the first row found, or an empty dict if no row exists yet
        return result.data[0] if result.data else {}
    except Exception as e:
        st.error(f"Database Load Error: {e}")
        return {}