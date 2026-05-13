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
            # Save to Supabase 'profiles' table
            profile_data = {
                "user_id": "Brian", # We'll keep this hardcoded for now until we add Auth
                "full_name": full_name,
                "email": email,
                "company_name": company,
                "industry": industry,
                "business_stage": stage
            }
            try:
                supabase.table("profiles").upsert(profile_data, on_conflict="user_id").execute()
                st.success("Foundation established! You are ready for the Soul Sprint.")
                st.balloons()
                # Store in session so we can bypass this screen next time
                st.session_state.onboarded = True
            except Exception as e:
                st.error(f"Error saving profile: {e}")