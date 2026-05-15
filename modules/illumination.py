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

    # 2. GENERATION LOGIC: HARD-CODED ARCHITECTURAL MANDATE
    if not st.session_state.final_soul_guide:
        if st.button("🔥 Illuminate the Master Soul Guide", use_container_width=True):
            with st.spinner("Synthesizing your Strategic Individual..."):
                
                # ENFORCED STRUCTURE (Based on your Gold Standard document)
                methodology = """
                ROLE: Godzspeed Soul Rebel Facilitator.
                TASK: Generate a Master Soul Guide. You MUST use the following headers exactly.
                
                MANDATORY SECTION HEADERS:
                1. SECTION 1: BRAND IDENTITY
                   - Big Idea (The rousing affirmation)
                   - What it Means (The deep narrative)
                   - Vision & Mission
                
                2. SECTION 2: TRANSFORMATION PROCESS
                   - Our Transformation Process (Detail the 3-step radical methodology)
                
                3. SECTION 3: SOUL ANCHORS
                   - Our Culture
                   - Our Values (Humility, Diversity, Curiosity, etc. explained)
                   - Beliefs (Written as 'We believe...')
                   - Behaviours (Written as 'We always...')
                
                4. SECTION 4: BRAND POSITIONING
                   - 1Soul Statement
                   - Our Offering (Staff, Clients, Communities)
                   - Target Audience (Detailed profiles of Allies and Partners)
                
                5. SECTION 5: BRAND EXPRESSION
                   - Slogan
                   - Brand Voice (Human, compelling, and hella smart)
                   - Brand Personality (The Caring Catalyst)
                
                6. SECTION 6: SOUL TIES
                   - Brand Legacy (What we want to be known for)
                   - Key Soul Markers (KPIs framed as 'Do I/Am I' audit questions)

                INSTRUCTION: 
                - Fill these sections using the Soul Audit data[cite: 190].
                - If data is missing for a section, provide a placeholder and add a 'FACILITATOR INQUIRY' at the bottom to ask the user for it[cite: 71, 72].
                """

                audit_context = f"""
                SOUL (PurpUS): {brand_data.get('purpus_summary')}
                MIND (Identity): {brand_data.get('brand_identity')}
                BODY (Experience): {brand_data.get('brand_experience')}
                BODY (Impact): {brand_data.get('brand_impact')}
                """
                
                guide = get_soul_rebel_consultant("Illuminate the Master Guide using the 6-Section Strategic Individual structure.", methodology + audit_context)
                st.session_state.final_soul_guide = guide
                save_brand_data(user_id, guide, chamber="soul_guide")
                st.rerun()

    # 3. MASTER WORKSPACE
    else:
        st.subheader("📜 The Strategic Individual Master Document")
        
        if "FACILITATOR INQUIRY" in st.session_state.final_soul_guide:
            st.warning("The Facilitator has questions to help deepen specific sections of your Guide.")
        
        edited_text = st.text_area(
            "Refine your strategic narrative:", 
            value=st.session_state.final_soul_guide, 
            height=600,
            key="guide_editor_field"
        )
        
        # 4. COLLABORATIVE REFINEMENT (THE SYNTHESIS ENGINE)
        st.write("---")
        st.write("💬 **Refine with the Facilitator**")
        guide_input = st.chat_input("Provide details to expand a specific section...")
        
        if guide_input:
            with st.spinner("Synthesizing and updating your Master Guide..."):
                # This methodology forces the AI to be an editor, not a re-writer
                update_methodology = """
                ROLE: Godzspeed Soul Rebel Facilitator.
                TASK: Synthesize the user's new input and UPDATE the Master Soul Guide.
                
                STRICT EDITORIAL RULES:
                1. DO NOT overwrite the entire document with a short response. 
                2. Use the new input to EXPAND and REFINE the relevant sections of the CURRENT DOCUMENT.
                3. Maintain the 6-SECTION structure: Identity, Transformation, Anchors, Positioning, Expression, Legacy.
                4. Ensure the new content matches the 'Human, compelling, and hella smart' tone.
                5. If this new info satisfies a 'FACILITATOR INQUIRY', remove that inquiry from the text.
                6. Output the FULL UPDATED DOCUMENT.
                """
                
                # We send the AI the CURRENT guide and the NEW details
                current_document = st.session_state.final_soul_guide
                
                # The AI synthesizes the answer INTO the document
                updated_guide = get_soul_rebel_consultant(
                    guide_input, 
                    f"{update_methodology}\n\nCURRENT DOCUMENT:\n{current_document}"
                )
                
                # Update Session and DB
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