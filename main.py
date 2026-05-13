import streamlit as st
from streamlit_supabase_auth import login_form, logout_button
from modules import discovery, profile_settings, wizard
from utils.supabase_db import supabase

# Set page configuration
st.set_page_config(page_title="Soul Rebel StratOS", layout="wide")

def check_profile_exists(user_id):
    """Checks Supabase for a profile belonging to the unique Auth UUID."""
    try:
        result = supabase.table("profiles").select("*").eq("user_id", user_id).execute()
        return len(result.data) > 0
    except Exception:
        return False

def main():
    # 1. THE SECURE GATEWAY
    # This handles the Login / Sign Up UI using your Supabase Project settings.
    # It will use the secrets you've already set up.
    session = login_form(
        url=st.secrets["SUPABASE_URL"],
        apiKey=st.secrets["SUPABASE_KEY"]
    )

    # If no one is logged in, stop here and show the login box
    if not session:
        st.title("🔥 Soul Rebel StratOS")
        st.info("The strategic command center for brands with a soul. Please log in to continue.")
        st.stop()

    # 2. CAPTURE AUTHENTICATED USER DATA
    user_id = session['user']['id']
    user_email = session['user']['email']

    # 3. PROFILE CHECK & NAVIGATION
    # We check if this specific UUID has completed the Wizard yet.
    if not check_profile_exists(user_id):
        # New user -> Force the Wizard to establish the foundation
        wizard.run(user_id)
    else:
        # Existing user -> Unlock the Workspace
        st.sidebar.title("Soul Rebel StratOS")
        st.sidebar.success(f"Rebel Active: {user_email}")
        
        # Logout button provided by the auth library
        logout_button()
        st.sidebar.write("---")

        choice = st.sidebar.radio("Navigate Workspace", 
            [
                "1. The Soul Sprint", 
                "2. Brand Guardian", 
                "3. O2O Analytics", 
                "⚙️ Profile Settings"
            ])

        st.sidebar.write("---")

        if choice == "1. The Soul Sprint":
            # Pass the user_id so they only see THEIR strategy
            discovery.run(user_id)
            
        elif choice == "2. Brand Guardian":
            st.title("🛡️ Brand Guardian")
            st.info("Aligning content with your Brand Soul.")
            
        elif choice == "3. O2O Analytics":
            st.title("📊 O2O Analytics")
            st.info("Module 3 coming soon.")
            
        elif choice == "⚙️ Profile Settings":
            # Pass the user_id for the 'Tombstone' and editing logic
            profile_settings.run(user_id)

if __name__ == "__main__":
    main()