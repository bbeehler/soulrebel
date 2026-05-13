import streamlit as st
from utils.supabase_db import supabase

def run():
    if "wizard_step" not in st.session_state:
        st.session_state.wizard_step = 1

    step = st.session_state.wizard_step
    
    # Visual Progress Indicator
    cols = st.columns(4)
    for i, col in enumerate(cols):
        if i + 1 <= step:
            col.write(f"**Step {i+1}** ✅" if i+1 < step else f"**Step {i+1}** 📍")
        else:
            col.write(f"Step {i+1}")
    
    st.write("---")

    # STEP 1: INDIVIDUAL
    if step == 1:
        st.subheader("Step 1: The Soul Behind the Movement")
        full_name = st.text_input("What is your full name?", value="Brian")
        email = st.text_input("Professional Email")
        if st.button("Continue to Venture"):
            st.session_state.temp_name = full_name
            st.session_state.temp_email = email
            st.session_state.wizard_step = 2
            st.rerun()

    # STEP 2: VENTURE
    elif step == 2:
        st.subheader("Step 2: The Venture Details")
        company = st.text_input("Company Name")
        industry = st.selectbox("Industry", ["Hospitality", "Technology", "Marketing", "Retail", "Other"])
        if st.button("Back"): st.session_state.wizard_step = 1; st.rerun()
        if st.button("Continue to Stage"):
            st.session_state.temp_company = company
            st.session_state.temp_industry = industry
            st.session_state.wizard_step = 3
            st.rerun()

    # STEP 3: STAGE & SCALE
    elif step == 3:
        st.subheader("Step 3: Growth Stage")
        stage = st.select_slider("Where are you currently?", options=["Concept", "MVP", "Scaling", "Established"])
        if st.button("Back"): st.session_state.wizard_step = 2; st.rerun()
        if st.button("Finalize Foundation"):
            st.session_state.temp_stage = stage
            st.session_state.wizard_step = 4
            st.rerun()

    # STEP 4: DATABASE SYNC
    elif step == 4:
        st.subheader("Step 4: Establish Your Command Center")
        st.write(f"Reviewing details for **{st.session_state.temp_company}**...")
        if st.button("Initialize StratOS"):
            profile_data = {
                "user_id": "Brian",
                "full_name": st.session_state.temp_name,
                "email": st.session_state.temp_email,
                "company_name": st.session_state.temp_company,
                "industry": st.session_state.temp_industry,
                "business_stage": st.session_state.temp_stage
            }
            supabase.table("profiles").upsert(profile_data, on_conflict="user_id").execute()
            st.session_state.authenticated = True
            st.session_state.wizard_step = 1 # Reset for next time
            st.balloons()
            st.rerun()