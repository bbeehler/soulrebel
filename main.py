import streamlit as st
from modules import discovery, profile_settings, wizard
from utils.supabase_db import supabase

# Set page configuration
st.set_page_config(page_title="Soul Rebel StratOS", layout="wide")

def check_profile_exists(user_id):
    """Checks Supabase to see if this user has completed onboarding."""
    try:
        result = supabase.table("profiles").select("*").eq("user_id", user_id).execute()
        return len(result.data) > 0
    except Exception:
        return False

def main():
    # 1. Initialize Authentication and Entry States
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    if "entry_mode" not in st.session_state:
        st.session_state.entry_mode = None

    # 2. LANDING PAGE: Only shown if not authenticated
    if not st.session_state.authenticated:
        st.title("🔥 Soul Rebel StratOS")
        st.subheader("Welcome to the Rebellion")
        st.write("The strategic command center for brands with a soul.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.info("### Existing Soul Rebels")
            if st.button("Log In to My Strategy", use_container_width=True):
                # For now, we simulate login by checking Brian's profile
                if check_profile_exists("Brian"):
                    st.session_state.authenticated = True
                    st.session_state.onboarded = True
                    st.rerun()
                else:
                    st.error("No profile found. Would you like to join the movement?")

        with col2:
            st.success("### New Movement Members")
            if st.button("Join the Rebellion", use_container_width=True):
                st.session_state.entry_mode = "wizard"

        # 3. WIZARD MODE: Triggered if they click 'Join'
        if st.session_state.entry_mode == "wizard":
            st.write("---")
            wizard.run()

    # 4. DASHBOARD: Only shown after authentication/wizard completion
    else:
        st.sidebar.title("Soul Rebel StratOS")
        st.sidebar.success("✅ Dashboard Engine Active")
        st.sidebar.write("---")

        choice = st.sidebar.radio("Navigate Workspace", 
            [
                "1. The Soul Sprint", 
                "2. Brand Guardian", 
                "3. O2O Analytics", 
                "⚙️ Profile Settings"
            ])

        st.sidebar.write("---")
        if st.sidebar.button("Log Out"):
            st.session_state.authenticated = False
            st.session_state.entry_mode = None
            st.rerun()

        if choice == "1. The Soul Sprint":
            discovery.run()
        elif choice == "2. Brand Guardian":
            st.title("🛡️ Brand Guardian")
            st.info("Aligning content with your Brand Soul.")
        elif choice == "3. O2O Analytics":
            st.title("📊 O2O Analytics")
        elif choice == "⚙️ Profile Settings":
            profile_settings.run()

if __name__ == "__main__":
    main()