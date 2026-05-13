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
    # --- HEADER SECTION ---
    # This renders at the top of the page regardless of login status
    st.title("🔥 Soul Rebel StratOS")
    st.subheader("The Strategic Command Center")
    st.write("Extracting the soul of your brand to fuel the rebellion.")
    st.write("---") # Visual separator

    # --- THE SECURE GATEWAY ---
    # By placing this here, it appears below the title and subheader
    session = login_form(
        url=st.secrets["SUPABASE_URL"],
        apiKey=st.secrets["SUPABASE_KEY"]
    )

    # If no one is logged in, stop execution here (preserving the header above)
    if not session:
        st.info("Welcome, Rebel. Please sign in or join the movement to access your strategy.")
        st.stop()

    # --- AUTHENTICATED SESSION DATA ---
    user_id = session['user']['id']
    user_email = session['user']['email']

    # --- NAVIGATION LOGIC ---
    if not check_profile_exists(user_id):
        # New user -> Force the Wizard to establish the foundation
        wizard.run(user_id)
    else:
        # Existing user -> Unlock the Workspace Sidebar
        st.sidebar.title("Soul Rebel StratOS")
        st.sidebar.success(f"Rebel Active: {user_email}")
        
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

        # Load Modules based on selection
        if choice == "1. The Soul Sprint":
            discovery.run(user_id)
            
        elif choice == "2. Brand Guardian":
            st.title("🛡️ Brand Guardian")
            st.info("Aligning content with your Brand Soul. Coming soon.")
            
        elif choice == "3. O2O Analytics":
            st.title("📊 O2O Analytics")
            st.info("Module 3: Online-to-Offline attribution. Coming soon.")
            
        elif choice == "⚙️ Profile Settings":
            profile_settings.run(user_id)

if __name__ == "__main__":
    main()