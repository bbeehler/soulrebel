import streamlit as st
from utils.supabase_db import supabase, load_brand_data, update_chamber_data

def run(user_id): # Fix: Now accepts user_id from main.py
    st.title("👤 Profile & Strategy Management")
    
    # --- SECTION 1: EDIT BRAND CHAMBERS ---
    st.subheader("Edit Strategy Chambers")
    
    # Load data specific to the logged-in user
    brand_data = load_brand_data(user_id)
    
    if brand_data:
        # Chamber 1 Edit
        with st.expander("Edit Chamber 1: PurpUS", expanded=False):
            new_purpus = st.text_area("Refine your PurpUS summary:", value=brand_data.get('purpus_summary', ""))
            if st.button("Save PurpUS Changes"):
                update_chamber_data(user_id, "purpus_summary", new_purpus)
                st.success("Chamber 1 updated.")

        # Chamber 2 Edit
        with st.expander("Edit Chamber 2: Brand Identity", expanded=False):
            new_identity = st.text_area("Refine your Brand Identity:", value=brand_data.get('brand_identity', ""))
            if st.button("Save Identity Changes"):
                update_chamber_data(user_id, "brand_identity", new_identity)
                st.success("Chamber 2 updated.")

        # Chamber 3 Edit
        with st.expander("Edit Chamber 3: Brand Experience", expanded=False):
            new_experience = st.text_area("Refine your Brand Experience:", value=brand_data.get('brand_experience', ""))
            if st.button("Save Experience Changes"):
                update_chamber_data(user_id, "brand_experience", new_experience)
                st.success("Chamber 3 updated.")

        # CHAMBER 4 EDIT: BRAND IMPACT
        with st.expander("Edit Chamber 4: Brand Impact", expanded=False):
            new_impact = st.text_area("Refine your Brand Impact strategy:", value=brand_data.get('brand_impact', ""))
            if st.button("Save Impact Changes"):
                update_chamber_data(user_id, "brand_impact", new_impact)
                st.success("Chamber 4 updated.")
    else:
        st.info("No brand strategy data found to edit yet. Start a Soul Sprint to generate insights.")

    st.write("---")

    # --- SECTION 2: THE TOMBSTONE (DANGER ZONE) ---
    st.subheader("⚠️ Danger Zone")
    with st.expander("Delete Account Data"):
        st.warning("This action is permanent. It will wipe your profile and all strategy chambers.")
        confirm_name = st.text_input("Type 'DELETE' to confirm:")
        
        if st.button("Permanently Wipe My Data"):
            if confirm_name == "DELETE":
                # Execute Wipes for the specific authenticated UUID
                supabase.table("profiles").delete().eq("user_id", user_id).execute()
                supabase.table("brand_strategy").delete().eq("user_id", user_id).execute()
                
                # Clear Session and trigger a logout/refresh
                st.session_state.clear() 
                st.success("Data wiped. Please log out or refresh.")
                st.rerun()
            else:
                st.error("Please type DELETE to confirm.")