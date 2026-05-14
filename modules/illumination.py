import streamlit as st
from utils.gemini_ai import get_soul_rebel_consultant
from utils.supabase_db import save_brand_data

def run(user_id):
    st.title("🕯️ Soul Illumination")
    st.subheader("Synthesizing your Brand Individual")

    brand_data = st.session_state.get('brand_soul', {})
    
    # Check if we have enough data to proceed
    chambers = ["purpus_summary", "brand_identity", "brand_experience", "brand_impact"]
    completed = [k for k in chambers if brand_data.get(k)]

    if len(completed) < 4:
        st.warning(f"You have completed {len(completed)}/4 chambers. Return to the Soul Sprint to finish extraction before Illumination.")
        if st.button("Back to Sprint"):
            st.session_state.page = "discovery"
            st.rerun()
        return

    st.info("The extraction is complete. The Individual is ready to be born.")

    if st.button("🔥 Generate Soul Guide", use_container_width=True):
        with st.spinner("Aligning Soul, Mind, and Body..."):
            # Construct the Master Context
            master_context = f"""
            SYSTEM METHODOLOGY: Godzspeed Soul Guide (Soul, Mind, Body).
            
            CHAMBER 1 (SOUL/PURPUS): {brand_data.get('purpus_summary')}
            CHAMBER 2 (MIND/IDENTITY): {brand_data.get('brand_identity')}
            CHAMBER 3 (BODY/EXPERIENCE): {brand_data.get('brand_experience')}
            CHAMBER 4 (BODY/IMPACT): {brand_data.get('brand_impact')}
            
            TASK: Synthesize these into a cohesive 'Soul Guide'. 
            Structure the response as:
            1. THE BIG IDEA (The singular hook).
            2. THE SOUL (The transcendental fire).
            3. THE MIND (Strategic persona).
            4. THE BODY (The ritual and the legacy).
            """
            
            soul_guide = get_soul_rebel_consultant("Synthesize my Soul Guide.", master_context)
            
            # Save the final synthesis to a new column or a specific row
            st.session_state.final_soul_guide = soul_guide
            st.success("Your Soul Guide has been illuminated.")

    if "final_soul_guide" in st.session_state:
        st.write("---")
        st.markdown(st.session_state.final_soul_guide)
        
        # Option to Export or Save
        st.button("📥 Download Soul Guide (PDF Coming Soon)")