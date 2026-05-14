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
    # Define options exactly as they appear in the radio
    nav_options = [
        "1. The Soul Sprint", 
        "2. ✨ The Soul Guide", 
        "3. Brand Guardian", 
        "4. O2O Analytics", 
        "⚙️ Profile Settings"
    ]

    # Check if a module requested a redirect
    if "target_page" in st.session_state:
        st.session_state.current_nav = st.session_state.target_page
        del st.session_state.target_page # Reset to avoid infinite loop

    # Initialize default navigation if empty
    if "current_nav" not in st.session_state:
        st.session_state.current_nav = "1. The Soul Sprint"

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
            
            # Map the current_nav to its index for the radio button
            try:
                curr_idx = nav_options.index(st.session_state.current_nav)
            except ValueError:
                curr_idx = 0

            # The key 'sidebar_radio' preserves the choice manually
            choice = st.sidebar.radio(
                "Navigate Workspace", 
                nav_options, 
                index=curr_idx,
                key="sidebar_radio"
            )
            
            # Update state to match user click
            st.session_state.current_nav = choice
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