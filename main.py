import streamlit as st
from streamlit_supabase_auth import login_form, logout_button
from modules import discovery, illumination, profile_settings, wizard
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
    # --- NAVIGATION REDIRECT LOGIC ---
    nav_options = [
        "1. The Soul Sprint", 
        "2. ✨ The Soul Guide", 
        "3. Brand Guardian", 
        "4. O2O Analytics", 
        "⚙️ Profile Settings"
    ]

    # Initialize current_nav if it doesn't exist
    if "current_nav" not in st.session_state:
        st.session_state.current_nav = "1. The Soul Sprint"

    # Check if a module (like illumination) requested a redirect
    if "target_page" in st.session_state:
        st.session_state.current_nav = st.session_state.target_page
        del st.session_state.target_page
        # We rerun immediately so the sidebar index below finds the new page
        st.rerun()

    # --- HEADER SECTION ---
    st.title("🔥 Soul Rebel StratOS")
    st.subheader("The Strategic Command Center")
    st.write("Extracting the soul of your brand to fuel the rebellion.")
    st.write("---") 

    # --- THE SECURE GATEWAY ---
    session = login_form(
        url=st.secrets["SUPABASE_URL"],
        apiKey=st.secrets["SUPABASE_KEY"]
    )

    if not session:
        st.info("Welcome, Rebel. Please sign in or join the movement to access your strategy.")
        st.stop()

    # --- AUTHENTICATED SESSION DATA ---
    user_id = session['user']['id']
    user_email = session['user']['email']

    # --- INSTANT ROUTING CHECK ---
    profile_exists = check_profile_exists(user_id)

    if not profile_exists:
        wizard.run(user_id)
    else:
        # --- SIDEBAR CONTROL PANEL ---
        with st.sidebar:
            st.title("Soul Rebel StratOS")
            st.success(f"Rebel Active: {user_email}")
            
            logout_button()
            st.write("---")
            
            # Find the index based on current session state
            try:
                curr_idx = nav_options.index(st.session_state.current_nav)
            except ValueError:
                curr_idx = 0

            # Use the index to force the radio button selection
            choice = st.radio(
                "Navigate Workspace", 
                nav_options, 
                index=curr_idx,
                key="sidebar_radio"
            )
            
            # If the user clicks the sidebar manually, update the current_nav
            if choice != st.session_state.current_nav:
                st.session_state.current_nav = choice
                st.rerun()
            
            st.write("---")

        # --- MAIN WORKSPACE LOGIC ---
        if st.session_state.current_nav == "1. The Soul Sprint":
            discovery.run(user_id)

        elif st.session_state.current_nav == "2. ✨ The Soul Guide":
            illumination.run(user_id)
            
        elif st.session_state.current_nav == "3. Brand Guardian":
            st.title("🛡️ Brand Guardian")
            st.info("Aligning content with your Brand Soul. Coming soon.")
            
        elif st.session_state.current_nav == "4. O2O Analytics":
            st.title("📊 O2O Analytics")
            st.info("Module 3: Online-to-Offline attribution. Coming soon.")
            
        elif st.session_state.current_nav == "⚙️ Profile Settings":
            profile_settings.run(user_id)

if __name__ == "__main__":
    main()