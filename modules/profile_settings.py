import streamlit as st
import time
from utils.supabase_db import supabase, load_brand_data, update_chamber_data

def run(user_id):
    st.title("👤 Profile & Strategy Management")
    st.caption("Refine your tactical strategy chambers or manage your StratOS ecosystem controls.")
    st.write("---")
    
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
                st.rerun()

        # Chamber 2 Edit
        with st.expander("Edit Chamber 2: Brand Identity", expanded=False):
            new_identity = st.text_area("Refine your Brand Identity:", value=brand_data.get('brand_identity', ""))
            if st.button("Save Identity Changes"):
                update_chamber_data(user_id, "brand_identity", new_identity)
                st.success("Chamber 2 updated.")
                st.rerun()

        # Chamber 3 Edit
        with st.expander("Edit Chamber 3: Brand Experience", expanded=False):
            new_experience = st.text_area("Refine your Brand Experience:", value=brand_data.get('brand_experience', ""))
            if st.button("Save Experience Changes"):
                update_chamber_data(user_id, "brand_experience", new_experience)
                st.success("Chamber 3 updated.")
                st.rerun()

        # CHAMBER 4 EDIT: BRAND IMPACT
        with st.expander("Edit Chamber 4: Brand Impact", expanded=False):
            new_impact = st.text_area("Refine your Brand Impact strategy:", value=brand_data.get('brand_impact', ""))
            if st.button("Save Impact Changes"):
                update_chamber_data(user_id, "brand_impact", new_impact)
                st.success("Chamber 4 updated.")
                st.rerun()
    else:
        st.info("No brand strategy data found to edit yet. Start a Soul Sprint to generate insights.")

    st.write("---")

    # --- SECTION 2: TACTICAL PHASE PURGE CENTER ---
    st.subheader("⚠️ Tactical Phase Deletion Matrix")
    st.caption("Flush individual operational layers from the database while keeping the rest of your architecture intact.")
    
    with st.expander("🪓 Open Targeted Reset Panel", expanded=False):
        purge_manifesto = st.checkbox("Phase 01 & 02: Clear Discovery Manifestos & Brand Chambers", value=False, key="p_wipe_manifesto")
        purge_soul_guide = st.checkbox("Phase 03: Clear Master Soul Guide Content Engine Context", value=False, key="p_wipe_soul")
        purge_calendar = st.checkbox("Phase 04: Flush Content Calendar Assets & Guardian Scans", value=False, key="p_wipe_cal")
        purge_analytics = st.checkbox("Phase 05: Clear O2O Analytics Logs (Inputs & Outcomes)", value=False, key="p_wipe_an")

        st.write(" ")
        if st.button("🪓 Execute Selective Phase Purge", type="secondary", use_container_width=True):
            if not any([purge_manifesto, purge_soul_guide, purge_calendar, purge_analytics]):
                st.warning("Please check at least one operational phase layer to execute a tactical purge.")
            else:
                with st.spinner("Executing targeted database deletions..."):
                    try:
                        if purge_manifesto:
                            supabase.table("brand_strategy").delete().eq("user_id", user_id).execute()
                        if purge_soul_guide:
                            supabase.table("brand_strategy").update({"soul_guide": None}).eq("user_id", user_id).execute()
                        if purge_calendar:
                            supabase.table("brand_content_items").delete().eq("user_id", user_id).execute()
                        if purge_analytics:
                            supabase.table("brand_digital_inputs").delete().eq("user_id", user_id).execute()
                            supabase.table("brand_offline_outcomes").delete().eq("user_id", user_id).execute()

                        st.success("Selected operational layers successfully purged from the database ecosystem!")
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Purge execution encountered a database error: {e}")

    st.write("---")

    # --- SECTION 3: THE TOMBSTONE (DANGER ZONE FACTORY RESET) ---
    st.subheader("🚨 Master System Reset")
    
    with st.expander("Delete Account Data / Full Factory Reset"):
        st.markdown(
            """
            <div style="background-color:#2a1b1b; padding:15px; border-radius:8px; border-left: 5px solid #e74c3c; margin-bottom:15px;">
                <p style="color:#ff9999; margin:0; font-weight:bold;">CRITICAL INFRASTRUCTURE ZONE</p>
                <p style="color:#fff; font-size:14px; margin:5px 0 0 0;">
                    This action is permanent. It will instantly drop all profiles, strategy chambers, calendar tracks, and analytical datasets connected to your user profile.
                </p>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        confirm_wipe = st.text_input(
            "To confirm this action, type **RESET ALL MY PHASES** in the validation box below:",
            placeholder="Type authorization string here...",
            key="master_wipe_confirm_input"
        )
        
        st.write(" ")
        is_disabled = (confirm_wipe != "RESET ALL MY PHASES")
        
        if st.button("🔥 Factory Reset Entire StratOS Profile", type="primary", use_container_width=True, disabled=is_disabled):
            with st.spinner("Dropping tables relational records across the entire grid..."):
                try:
                    # 1. Clear relational child tables first to respect integrity constraints
                    supabase.table("brand_content_items").delete().eq("user_id", user_id).execute()
                    supabase.table("brand_digital_inputs").delete().eq("user_id", user_id).execute()
                    supabase.table("brand_offline_outcomes").delete().eq("user_id", user_id).execute()
                    
                    # 2. Drop parent profile data and strategic assets
                    supabase.table("profiles").delete().eq("user_id", user_id).execute()
                    supabase.table("brand_strategy").delete().eq("user_id", user_id).execute()
                    
                    st.success("System framework wiped clean. Restarting StratOS application runtime...")
                    time.sleep(1.5)
                    
                    # 3. Clear transient session vectors and bounce user straight to onboarding initialization wizard
                    st.session_state.clear() 
                    st.session_state.current_nav = "Wizard"
                    st.rerun()
                except Exception as e:
                    st.error(f"Master reset process failed: {e}")