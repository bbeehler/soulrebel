import streamlit as st
import time
from utils.gemini_ai import get_soul_rebel_consultant
from utils.supabase_db import save_brand_data, load_brand_data

def run(user_id):
    st.title("✨ Phase 03: Illumination")
    st.caption("Establishing the Strategic Individual through a high-fidelity Master Document.")
    st.write("---")
    
    # 1. LOAD AUDIT DATA
    db_data = load_brand_data(user_id)
    brand_data = db_data if db_data else {}
    
    if "final_soul_guide" not in st.session_state:
        st.session_state.final_soul_guide = brand_data.get("soul_guide", "")

    # 2. GENERATION LOGIC: ARCHITECTURAL MIMICRY
    if not st.session_state.final_soul_guide:
        if st.button("🔥 Illuminate the Master Soul Guide", use_container_width=True):
            with st.spinner("Synthesizing your Strategic Individual..."):
                
                # THE PROFESSIONAL ARCHITECTURE (No Black Planning Project Content Used)
                methodology = """
                ROLE: Godzspeed Soul Rebel Facilitator.
                TASK: Generate a Master Soul Guide following a professional 'Strategic Individual' framework. 
                
                STRUCTURE REQUIREMENTS:
                - Section 1: The Core Identity (The big idea, narrative meaning, and long-term vision/mission).
                - Section 2: The Transformation Methodology (A clear 3-step process for how this brand changes its industry).
                - Section 3: Cultural Anchors (Values converted into 'We Believe' and 'We Always' actionable behaviors).
                - Section 4: Market Positioning (Core function statement and segmented target audience profiles).
                - Section 5: Brand Expression (Strategic slogan, voice guidelines, and core personality).
                - Section 6: Strategic Legacy (Future impact and KPIs framed as 'Do I/Am I' self-audit questions).

                TONE: Human, compelling, authoritative, and sophisticated.
                
                IMPORTANT:
                1. Use the Soul Audit data as the exclusive fuel.
                2. If the data for a section is 'light' or missing, do not hallucinate. 
                3. Append a 'FACILITATOR INQUIRY' at the end to ask the user for specific details needed to complete the section.
                """

                audit_context = f"""
                SOUL (PurpUS): {brand_data.get('purpus_summary')}
                MIND (Identity): {brand_data.get('brand_identity')}
                BODY (Experience): {brand_data.get('brand_experience')}
                BODY (Impact): {brand_data.get('brand_impact')}
                """
                
                guide = get_soul_rebel_consultant("Illuminate the Master Guide.", methodology + audit_context)
                st.session_state.final_soul_guide = guide
                save_brand_data(user_id, guide, chamber="soul_guide")
                st.rerun()

    # 3. MASTER WORKSPACE
    else:
        st.subheader("📜 The Strategic Individual Master Document")
        
        # Highlight if the AI is waiting for more info
        if "FACILITATOR INQUIRY" in st.session_state.final_soul_guide:
            st.warning("The Facilitator has questions to help deepen specific sections of your Guide.")
        
        edited_text = st.text_area(
            "Refine your strategic narrative:", 
            value=st.session_state.final_soul_guide, 
            height=600,
            key="guide_editor_field"
        )
        
        # 4. COLLABORATIVE REFINEMENT
        st.write("---")
        st.write("💬 **Refine with the Facilitator**")
        guide_input = st.chat_input("Answer inquiries or provide more detail here...")
        
        if guide_input:
            with st.spinner("Integrating depth..."):
                update_methodology = "Update the Master Document with the new details provided, maintaining the 6-section structure."
                updated_guide = get_soul_rebel_consultant(guide_input, update_methodology + st.session_state.final_soul_guide)
                st.session_state.final_soul_guide = updated_guide
                save_brand_data(user_id, updated_guide, chamber="soul_guide")
                st.rerun()

        # 5. ACTION CONTROLS
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("💾 Save Strategy", use_container_width=True):
                save_brand_data(user_id, edited_text, chamber="soul_guide")
                st.success("Soul Guide Saved.")
        with c2:
            if st.button("🗑️ Reset Guide", use_container_width=True):
                save_brand_data(user_id, None, chamber="soul_guide")
                st.session_state.final_soul_guide = ""
                st.rerun()
        with c3:
            # Placeholder for future functionality
            st.button("📄 Export PDF", use_container_width=True, disabled=True)