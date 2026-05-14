import streamlit as st
import time
from utils.gemini_ai import get_soul_rebel_consultant
from utils.supabase_db import save_brand_data, load_brand_data

def run(user_id):
    st.title("✨ The Soul Guide")
    st.write("---")

    # 1. Check for existing Soul Guide in Session State or DB
    if "final_soul_guide" not in st.session_state:
        db_data = load_brand_data(user_id)
        # Pulling specifically from the new column in brand_strategy
        st.session_state.final_soul_guide = db_data.get("soul_guide", "") if db_data else ""

    brand_data = st.session_state.get('brand_soul', {})
    
    # 2. Requirements Check
    chambers = ["purpus_summary", "brand_identity", "brand_experience", "brand_impact"]
    missing = [k for k in chambers if not brand_data.get(k)]

    if missing and not st.session_state.final_soul_guide:
        st.warning("The Individual is not yet fully formed. Please complete the Soul Sprint chambers first.")
        return

    # 3. GENERATION INTERFACE
    if not st.session_state.final_soul_guide:
        st.info("The four chambers are aligned. The Individual is ready for Illumination.")
        if st.button("🔥 Illuminate the Soul Guide", use_container_width=True):
            with st.spinner("Weaving the Soul, Mind, and Body..."):
                # Master Synthesis Prompt
                illumination_prompt = f"""
                You are the Soul Rebel Consultant. Synthesize a Godzspeed Soul Guide based on:
                
                SOUL (PurpUS): {brand_data.get('purpus_summary')}
                MIND (Identity): {brand_data.get('brand_identity')}
                BODY (Experience): {brand_data.get('brand_experience')}
                BODY (Impact): {brand_data.get('brand_impact')}
                
                Deliver a cohesive strategic narrative including:
                - THE BIG IDEA
                - THE SOUL (Why/Fire)
                - THE MIND (Persona/Voice)
                - THE BODY (Ritual/Legacy)
                """
                
                guide_content = get_soul_rebel_consultant("Illuminate my Soul Guide.", illumination_prompt)
                
                # Persist to Session State and Database
                st.session_state.final_soul_guide = guide_content
                save_brand_data(user_id, guide_content, chamber="soul_guide")
                st.rerun()

    # 4. THE MASTER DOCUMENT WORKSPACE
    else:
        st.subheader("📜 Master Strategy Document")
        
        # This text area allows the user to refine the AI's output
        edited_guide = st.text_area(
            "Final Soul Guide Content:", 
            value=st.session_state.final_soul_guide, 
            height=600,
            key="soul_guide_editor"
        )
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("💾 Save to Profile", use_container_width=True):
                st.session_state.final_soul_guide = edited_guide
                save_brand_data(user_id, edited_guide, chamber="soul_guide")
                st.success("Strategy Saved.")
        
        with col2:
            if st.button("📄 Prepare PDF", use_container_width=True):
                st.toast("PDF Export logic warming up...")
        
        with col3:
            if st.button("🗑️ Reset Guide", use_container_width=True):
                # Using a session state flag for confirmation is safer
                st.session_state.confirm_reset = True
                
            if st.session_state.get("confirm_reset"):
                st.warning("This will delete the synthesized guide. Are you sure?")
                if st.button("Yes, Clear Master Guide"):
                    st.session_state.final_soul_guide = ""
                    save_brand_data(user_id, "", chamber="soul_guide")
                    st.session_state.confirm_reset = False
                    st.rerun()