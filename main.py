import streamlit as st
import time
from streamlit_supabase_auth import login_form, logout_button
from modules import discovery, illumination, guardian, analytics, profile_settings, wizard
from utils.supabase_db import supabase

# Set page configuration
st.set_page_config(page_title="Scriptly Labs OS", layout="wide")

def check_profile_exists(user_id):
    """Checks Supabase for a profile belonging to the unique Auth UUID."""
    try:
        result = supabase.table("profiles").select("*").eq("user_id", user_id).execute()
        return len(result.data) > 0
    except Exception:
        return False

def main():
    # --- ECOSYSTEM VIEWPORT INITIALIZATION ---
    if "ecosystem_sync_version" not in st.session_state:
        st.session_state.ecosystem_sync_version = 0

    # 1. Define Rebranded Navigation Options
    nav_options = [
        "1. Discovery Audit", 
        "2. Master Voice Blueprint", 
        "3. Brand Guardian", 
        "4. O2O Analytics", 
        "⚙️ Profile Settings"
    ]

    # --- HEADER SECTION ---
    st.title("Scriptly Labs OS")
    st.subheader("The Strategic Command Center")
    st.write("Engineering high-fidelity brand authority engines and compliance workflows.")
    st.write("---") 

    # --- THE SECURE GATEWAY ---
    session = login_form(
        url=st.secrets["SUPABASE_URL"],
        apiKey=st.secrets["SUPABASE_KEY"]
    )

    if not session:
        st.info("Welcome to Scriptly Labs. Please sign in or create an account to access your workspace.")
        st.stop()

    # --- AUTHENTICATED ZONE ---
    user_id = session['user']['id']
    user_email = session['user']['email']

    # =========================================================================
    # CRITICAL INTERCEPT: FORCE WIDGET STATE RESET BEFORE SIDEBAR RENDERS
    # =========================================================================
    if "target_page" in st.session_state:
        target = st.session_state.target_page
        
        # Handle backward-compatible remapping if string names from legacy modules fire
        if target == "2. The Soul Guide":
            target = "2. Master Voice Blueprint"
        elif target == "1. The Soul Sprint":
            target = "1. Discovery Audit"
            
        # Override the persistent session states
        st.session_state.current_nav = target
        
        # Overwrite internal widget cache key directly so st.radio initializes here
        st.session_state["sidebar_radio"] = target
        
        # Update the database profile position map
        try:
            supabase.table("profiles").update({"last_nav": target}).eq("user_id", user_id).execute()
        except:
            pass
            
        del st.session_state.target_page
        st.rerun()
    # =========================================================================

    # --- PERSISTENCE LOGIC: Initial Load ---
    if "current_nav" not in st.session_state:
        try:
            # Check DB for last saved position
            response = supabase.table("profiles").select("last_nav").eq("user_id", user_id).execute()
            if response.data and response.data[0].get("last_nav"):
                db_nav = response.data[0]["last_nav"]
                
                # Dynamic remapping fallback for existing database rows
                if db_nav == "2. The Soul Guide":
                    db_nav = "2. Master Voice Blueprint"
                elif db_nav == "1. The Soul Sprint":
                    db_nav = "1. Discovery Audit"
                    
                st.session_state.current_nav = db_nav
            else:
                st.session_state.current_nav = "1. Discovery Audit"
        except Exception:
            st.session_state.current_nav = "1. Discovery Audit"

    # 3. ROUTING CHECK
    profile_exists = check_profile_exists(user_id)

    if not profile_exists:
        wizard.run(user_id)
    else:
        # --- SIDEBAR CONTROL PANEL ---
        with st.sidebar:
            st.title("Scriptly Labs OS")
            st.success(f"Active Account: {user_email}")
            
            logout_button()
            st.write("---")
            
            try:
                curr_idx = nav_options.index(st.session_state.current_nav)
            except ValueError:
                curr_idx = 0

            choice = st.radio(
                "Navigate Workspace", 
                nav_options, 
                index=curr_idx,
                key="sidebar_radio"
            )
            
            # If the user manually clicks the sidebar, update session AND DB
            if choice != st.session_state.current_nav:
                st.session_state.current_nav = choice
                try:
                    supabase.table("profiles").update({"last_nav": choice}).eq("user_id", user_id).execute()
                except:
                    pass
                st.rerun()
            
            st.write("---")

        # --- DYNAMIC HARDWARE VIEWPORT REPAINT LAYER ---
        with st.container(key=f"ecosystem_viewport_v_{st.session_state.ecosystem_sync_version}"):
            if st.session_state.current_nav == "1. Discovery Audit":
                discovery.run(user_id)

            elif st.session_state.current_nav == "2. Master Voice Blueprint":
                illumination.run(user_id)
                
            elif st.session_state.current_nav == "3. Brand Guardian":
                guardian.run(user_id)
                
            elif st.session_state.current_nav == "4. O2O Analytics":
                analytics.run(user_id)
                
            elif st.session_state.current_nav == "⚙️ Profile Settings":
                profile_settings.run(user_id)

if __name__ == "__main__":
    main()