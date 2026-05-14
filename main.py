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
    # 1. Define Navigation Options
    # These strings must be matched EXACTLY by any redirect buttons in your modules.
    nav_options = [
        "1. The Soul Sprint", 
        "2. ✨ The Soul Guide", 
        "3. Brand Guardian", 
        "4. O2O Analytics", 
        "⚙️ Profile Settings"
    ]

    # --- HEADER SECTION ---
    st.title("🔥 Soul Rebel StratOS")
    st.subheader("The Strategic Command Center")
    st.write("Extracting the soul of your brand to fuel the rebellion.")
    st.write("---") 

    # --- THE SECURE GATEWAY ---
    # The login form must run before any other logic to establish the session.
    session = login_form(
        url=st.secrets["SUPABASE_URL"],
        apiKey=st.secrets["SUPABASE_KEY"]
    )

    if not session:
        st.info("Welcome, Rebel. Please sign in or join the movement to access your strategy.")
        st.stop()

    # --- AUTHENTICATED ZONE ---
    # Everything below this point only runs if the user is logged in.
    user_id = session['user']['id']
    user_email = session['user']['email']

    # 2. HANDLE PROGRAMMATIC REDIRECTS
    # This checks if a module (like Illumination) requested a page change.
    if "target_page" in st.session_state:
        st.session_state.current_nav = st.session_state.target_page
        del st.session_state.target_page
        st.rerun()

    # Initialize default navigation if it doesn't exist in the session
    if "current_nav" not in st.session_state:
        st.session_state.current_nav = "1. The Soul Sprint"

    # 3. INSTANT ROUTING CHECK (New User Wizard vs. Dashboard)
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
            
            # Map the current_nav string to its numeric index for the radio widget
            try:
                curr_idx = nav_options.index(st.session_state.current_nav)
            except ValueError:
                curr_idx = 0

            # Create the navigation radio button
            choice = st.radio(
                "Navigate Workspace", 
                nav_options, 
                index=curr_idx,
                key="sidebar_radio"
            )
            
            # If the user clicks the sidebar manually, update the current_nav and rerun
            if choice != st.session_state.current_nav:
                st.session_state.current_nav = choice
                st.rerun()
            
            st.write("---")

        # --- MAIN WORKSPACE LOGIC ---
        # Route the user to the correct module based on the session state
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