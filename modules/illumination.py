import streamlit as st
import time
from utils.gemini_ai import get_soul_rebel_consultant
from utils.supabase_db import save_brand_data, load_brand_data

def run(user_id):
    st.title("✨ Phase 03: Illumination")
    st.caption("To illuminate means to bring to light. We are unearthing and igniting your purpose-driven brand.")
    st.write("---")
    
    # 1. LOAD DATA
    db_data = load_brand_data(user_id)
    brand_data = db_data if db_data else {}
    
    if "final_soul_guide" not in st.session_state:
        st.session_state.final_soul_guide = brand_data.get("soul_guide", "")

    # 2. COLLABORATIVE BUILDER
    with st.expander("🛠️ Soul Guide Builder (Collaborative Unearthing)", expanded=not st.session_state.final_soul_guide):
        st.info("If the Soul Audit was light, use this chat to deepen the vision before generating the Master Document.")
        
        if "guide_messages" not in st.session_state:
            st.session_state.guide_messages = []

        # Display Builder History
        for msg in st.session_state.guide_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        guide_input = st.chat_input("Add more depth or specific details for the Master Guide...")
        
        if guide_input:
            st.session_state.guide_messages.append({"role": "user", "content": guide_input})
            with st.chat_message("assistant"):
                with st.spinner("Synthesizing depth..."):
                    builder_methodology = "You are the Soul Rebel Facilitator. Help the user reach the Gold Standard structure (Identity, Transformation, Anchors, Positioning, Expression, Legacy)."
                    response = get_soul_rebel_consultant(guide_input, builder_methodology + str(brand_data))
                    st.session_state.guide_messages.append({"role": "assistant", "content": response})
                    st.rerun()

    # 3. GENERATION PHASE (The Gold Standard)
    if not st.session_state.final_soul_guide:
        if st.button("🔥 Illuminate the Gold-Standard Soul Guide", use_container_width=True):
            with st.spinner("Igniting your Strategic Individual..."):
                
                # BAKED-IN GOLD STANDARD METHODOLOGY
                methodology = """
                TASK: Generate the 'Soul Guide: Strategic Individual' master document.
                BLUEPRINT: You must follow the 'Black Planning Project' structure exactly.

                REQUIRED SECTIONS:
                1. BRAND IDENTITY: Big Idea (rousing affirmation), What it Means (narrative dive), Vision, and Mission.
                2. THE TRANSFORMATION PROCESS: 3-step methodology (e.g., Blueprint, Advocate, Inform).
                3. SOUL ANCHORS: Values, Beliefs (We believe...), and Behaviours (We always...).
                4. BRAND POSITIONING: 1Soul Statement and Target Audience (Allies vs. Partners).
                5. BRAND EXPRESSION: Slogan, Voice (Human, compelling, hella smart), and Personality (The Catalyst).
                6. SOUL TIES: Brand Legacy and Key Soul Markers (KPIs as 'Do I' questions).
                """

                # Combine Audit data with new Builder chat data
                combined_context = f"Audit Data: {brand_data}\n\nBuilder Chat: {st.session_state.guide_messages}"
                
                guide = get_soul_rebel_consultant("Illuminate my Soul Guide following the Black Planning Project standard.", methodology + combined_context)
                st.session_state.final_soul_guide = guide
                save_brand_data(user_id, guide, chamber="soul_guide")
                st.rerun()
    
    # 4. THE WORKSPACE
    else:
        st.subheader("📜 The Soul Guide (Master Document)")
        edited_text = st.text_area(
            "Finalize your Strategic Individual narrative:", 
            value=st.session_state.final_soul_guide, 
            height=600,
            key="guide_editor_field"
        )
        
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("💾 Save Strategy", use_container_width=True):
                save_brand_data(user_id, edited_text, chamber="soul_guide")
                st.success("Soul Guide Saved.")
        with c2:
            if st.button("⬅️ Back to Builder", use_container_width=True):
                st.session_state.final_soul_guide = ""
                st.rerun()
        with c3:
            if st.button("🗑️ Reset All", use_container_width=True):
                save_brand_data(user_id, None, chamber="soul_guide")
                st.session_state.final_soul_guide = ""
                st.session_state.guide_messages = []
                st.rerun()