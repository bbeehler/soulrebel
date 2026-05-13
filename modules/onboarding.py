import streamlit as st
from utils.supabase_db import supabase

def run():
    st.title("🚀 Project Onboarding")
    st.write("Before we dive into the Soul Sprint, let's establish the foundation of your venture.")

    with st.form("intake_form"):
        st.subheader("Individual & Business Details")
        col1, col2 = st.columns(2)
        
        with col1:
            full_name = st.text_input("Full Name", value=st.session_state.get('user_name', "Brian"))
            email = st.text_input("Professional Email")
            company = st.text_input("Company Name")
            
        with col2:
            industry = st.selectbox("Industry", ["Hospitality", "Technology", "Marketing", "Retail", "Other"])
            stage = st.select_slider("Business Stage", options=["Concept", "MVP", "Scaling", "Established"])
            linkedin = st.text_input("LinkedIn Profile (Optional)")

        submitted = st.form_submit_button("Initialize StratOS")
        
        if submitted:
            # Prepare data for Supabase
            profile_data = {
                "user_id": "Brian", # Unique ID for session tracking
                "full_name": full_name,
                "email": email,
                "company_name": company,
                "industry": industry,
                "business_stage": stage
            }
            
            try:
                # Save to Supabase 'profiles' table
                supabase.table("profiles").upsert(profile_data, on_conflict="user_id").execute()
                
                # Update Session State to flip the 'onboarded' gate
                st.session_state.onboarded = True
                
                st.success("Foundation established! You are ready for the Soul Sprint.")
                st.balloons()
                
                # Force a rerun to show the sidebar menu immediately
                st.rerun()
                
            except Exception as e:
                st.error(f"Error saving profile: {e}")