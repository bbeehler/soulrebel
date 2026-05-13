import streamlit as st
from modules import onboarding, discovery, profile_settings
from utils.supabase_db import supabase

# Set page configuration
st.set_page_config(page_title="Soul Rebel StratOS", layout="wide")

# Dashboard connection indicator
st.sidebar.success("✅ Dashboard Engine Active")

def check_profile_exists(user_id):
    """Checks Supabase to see if this user has completed onboarding."""
    try:
        result = supabase.table("profiles").select("*").eq("user_id", user_id).execute()
        return len(result.data) > 0
    except Exception:
        # If the table doesn't exist yet or connection fails, default to False
        return False

def main():
    # Initialize session state for onboarding if not already present
    if "onboarded" not in st.session_state:
        # Using 'Brian' as the unique ID for now
        st.session_state.onboarded = check_profile_exists("Brian")

    st.sidebar.title("Soul Rebel StratOS")
    st.sidebar.write("---")

    # LOGIC GATE: Force Onboarding if no profile exists
    if not st.session_state.onboarded:
        onboarding.run()
    else:
        # Main Navigation Workspace
        # Added Gear icon for Profile Settings as the Control Room
        choice = st.sidebar.radio("Navigate Workspace", 
            [
                "1. The Soul Sprint", 
                "2. Brand Guardian", 
                "3. O2O Analytics", 
                "⚙️ Profile Settings"
            ])

        st.sidebar.write("---")
        
        # Navigation logic
        if choice == "1. The Soul Sprint":
            discovery.run()
            
        elif choice == "2. Brand Guardian":
            st.title("🛡️ Brand Guardian")
            st.info("Module 2: Aligning your content with your Brand Soul. Coming soon.")
            
        elif choice == "3. O2O Analytics":
            st.title("📊 O2O Analytics")
            st.info("Module 3: Online-to-Offline attribution and KPIs. Coming soon.")
            
        elif choice == "⚙️ Profile Settings":
            # This is where editing and the 'Tombstone' deletion now live
            profile_settings.run()

if __name__ == "__main__":
    main()