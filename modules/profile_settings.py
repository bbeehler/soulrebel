import streamlit as st
from utils.supabase_db import supabase, load_brand_data, update_chamber_data

def run():
    st.title("👤 Profile & Strategy Management")
    
    # --- SECTION 1: EDIT BRAND CHAMBERS ---
    st.subheader("Edit Strategy Chambers")
    brand_data = load_brand_data("Brian")
    
    if brand_data:
        # Chamber 1 Edit
        with st.expander("Edit Chamber 1: PurpUS", expanded=False):
            new_purpus = st.text_area("Refine your PurpUS summary:", value=brand_data.get('purpus_summary', ""))
            if st.button("Save PurpUS Changes"):
                update_chamber_data("Brian", "purpus_summary", new_purpus)
                st.success("Chamber 1 updated.")

        # Chamber 2 Edit
        with st.expander("Edit Chamber 2: Brand Identity", expanded=False):
            new_identity = st.text_area("Refine your Brand Identity:", value=brand_data.get('brand_identity', ""))
            if st.button("Save Identity Changes"):
                update_chamber_data("Brian", "brand_identity", new_identity)
                st.success("Chamber 2 updated.")
    else:
        st.info("No brand strategy data found to edit yet.")

    st.write("---")

    # --- SECTION 2: THE TOMBSTONE (DANGER ZONE) ---
    st.subheader("⚠️ Danger Zone")
    with st.expander("Delete Account & Data"):
        st.warning("This action is permanent. It will wipe your profile and all strategy chambers.")
        confirm_name = st.text_input("Type 'DELETE' to confirm:")
        
        if st.button("Permanently Wipe My Data"):
            if confirm_name == "DELETE":
                # Execute Wipes
                supabase.table("profiles").delete().eq("user_id", "Brian").execute()
                supabase.table("brand_strategy").delete().eq("user_id", "Brian").execute()
                
                # Clear Session
                st.session_state.onboarded = False
                st.rerun()
            else:
                st.error("Please type DELETE to confirm.")