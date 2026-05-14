import streamlit as st
import time
from utils.gemini_ai import get_soul_rebel_consultant
from utils.supabase_db import save_brand_data

def run(user_id):
    st.title("✨ The Soul Guide")
    st.write("---")

    # 1. Access the unearthed data
    brand_data = st.session_state.get('brand_soul', {})
    
    # 2. Validation Gate
    chambers = ["purpus_summary", "brand_identity", "brand_experience", "brand_impact"]
    missing = [label for label, key in [
        ("PurpUS", "purpus_summary"), 
        ("Identity", "brand_identity"), 
        ("Experience", "brand_experience"), 
        ("Impact", "brand_impact")
    ] if not brand_data.get(key)]

    if missing:
        st.warning(f"The Individual is not yet fully formed. Please complete the following chambers in the Soul Sprint: {', '.join(missing)}")
        if st.button("Return to the Sprint"):
            st.session_state.page = "discovery" # If using page state
            st.rerun()
        return

    # 3. The Illumination Interface
    col1, col2 = st.columns([2, 1])

    with col2:
        st.info("### The Godzspeed Framework\nWe are now fusing your Soul, Mind, and Body into a single Strategic Individual.")
        

    with col1:
        if st.button("🔥 Illuminate the Soul Guide", use_container_width=True):
            with st.spinner("Synthesizing the Brand Individual..."):
                
                # The "Master Weaver" Prompt
                illumination_prompt = f"""
                You are the Soul Rebel Consultant. You have extracted four core chambers of a brand.
                Now, synthesize them into a formal 'Soul Guide' using the Godzspeed methodology.
                
                DATA INPUTS:
                - SOUL (The Fire): {brand_data.get('purpus_summary')}
                - MIND (The Persona): {brand_data.get('brand_identity')}
                - BODY (The Ritual): {brand_data.get('brand_experience')}
                - BODY (The Legacy): {brand_data.get('brand_impact')}
                
                STRUCTURE YOUR RESPONSE:
                1. THE BIG IDEA: A singular, visceral hook that defines this brand's existence.
                2. THE SOUL: Define the transcendental 'Why' and the internal fire.
                3. THE MIND: Define the Strategic Persona—how the Soul thinks and speaks.
                4. THE BODY: Define the Brand Ritual (Experience) and the ultimate Social Footprint (Impact).
                """
                
                final_guide = get_soul_rebel_consultant("Illuminate my Soul Guide.", illumination_prompt)
                st.session_state.soul_guide_content = final_guide
                
                # Optional: Save this synthesis back to Supabase in a dedicated 'soul_guide' column
                # save_brand_data(user_id, final_guide, chamber="soul_guide")

        if "soul_guide_content" in st.session_state:
            st.markdown("### 📜 Your Illuminated Soul Guide")
            st.write("---")
            st.markdown(st.session_state.soul_guide_content)
            
            st.write("---")
            c1, c2 = st.columns(2)
            with c1:
                st.button("📄 Export to PDF (Coming Soon)")
            with c2:
                if st.button("🔄 Re-Illuminate"):
                    del st.session_state.soul_guide_content
                    st.rerun()