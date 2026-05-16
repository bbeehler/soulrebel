import streamlit as st
import time
from utils.gemini_ai import get_soul_rebel_consultant
from utils.supabase_db import save_brand_data, load_brand_data

def run(user_id):
    st.title("✨ Phase 03: Illumination")
    st.caption("Forging the Strategic Individual: One Section at a Time.")
    st.write("---")
    
    # 1. LOAD AUDIT DATA & INITIALIZE STATE
    db_data = load_brand_data(user_id)
    brand_data = db_data if db_data else {}
    
    # Define the 6-Section sequence
    guide_sections = [
        {"id": "identity", "label": "SECTION 1: BRAND IDENTITY", "focus": "Big Idea, Narrative Meaning, Vision, Mission"},
        {"id": "transformation", "label": "SECTION 2: TRANSFORMATION PROCESS", "focus": "The 3-Step Radical Methodology"},
        {"id": "anchors", "label": "SECTION 3: SOUL ANCHORS", "focus": "Values, Beliefs (We believe), Behaviours (We always)"},
        {"id": "positioning", "label": "SECTION 4: BRAND POSITIONING", "focus": "1Soul Statement, Offerings, Target Audience Allies/Partners"},
        {"id": "expression", "label": "SECTION 5: BRAND EXPRESSION", "focus": "Slogan, Voice (Human/Smart), Personality (Catalyst)"},
        {"id": "legacy", "label": "SECTION 6: SOUL TIES", "focus": "Brand Legacy & Key Soul Markers (Do I/Am I KPIs)"}
    ]

    if "guide_step_idx" not in st.session_state:
        st.session_state.guide_step_idx = 0
    if "final_soul_guide_parts" not in st.session_state:
        # Load existing guide parts if they exist
        st.session_state.final_soul_guide_parts = brand_data.get("soul_guide_parts", {})

    current_idx = st.session_state.guide_step_idx
    
    # Check if we've completed all sections
    if current_idx >= len(guide_sections):
        st.success("🎉 All sections committed! Your Strategic Individual is complete.")
        full_guide = "\n\n".join(st.session_state.final_soul_guide_parts.values())
        st.text_area("Final Master Document", value=full_guide, height=600)
        if st.button("🗑️ Reset and Re-Illuminate"):
            st.session_state.guide_step_idx = 0
            st.session_state.final_soul_guide_parts = {}
            st.rerun()
        return

    current_section = guide_sections[current_idx]

    # 2. WORKSPACE LAYOUT
    col1, col2 = st.columns([3, 2])

    with col1:
        st.subheader(current_section["label"])
        st.caption(f"Strategic Focus: {current_section['focus']}")
        
        # Initial Draft Generation for this section only
        section_key = current_section["id"]
        if section_key not in st.session_state.final_soul_guide_parts:
            with st.spinner(f"Drafting {current_section['label']} from Audit data..."):
                methodology = f"""
                ROLE: Godzspeed Soul Rebel Facilitator.
                TASK: Draft ONLY {current_section['label']}.
                FOCUS: {current_section['focus']}
                SOURCE: Use the Soul Audit data provided. 
                TONE: Human, compelling, and hella smart.
                """
                audit_context = str(brand_data)
                draft = get_soul_rebel_consultant(f"Draft {current_section['label']}", methodology + audit_context)
                st.session_state.final_soul_guide_parts[section_key] = draft

        # The Workspace for the current section
        current_draft = st.session_state.final_soul_guide_parts[section_key]
        edited_section = st.text_area("Refine this section:", value=current_draft, height=450, key=f"edit_{section_key}")
        st.session_state.final_soul_guide_parts[section_key] = edited_section

        # Collaborative Synthesis Loop
        st.write("---")
        guide_input = st.chat_input(f"Add more detail or refine {current_section['label']}...")
        if guide_input:
            with st.spinner("Synthesizing..."):
                update_prompt = f"Update this section only: {current_section['label']}. Maintain the professional tone."
                new_draft = get_soul_rebel_consultant(guide_input, update_prompt + "\n\nCURRENT SECTION:\n" + edited_section)
                st.session_state.final_soul_guide_parts[section_key] = new_draft
                st.rerun()

    with col2:
        st.subheader("🧬 Guide Progress")
        # Display completed sections as uneditable history
        for i, section in enumerate(guide_sections):
            if i < current_idx:
                with st.expander(f"✅ {section['label']}", expanded=False):
                    st.markdown(st.session_state.final_soul_guide_parts.get(section['id'], ""))
            elif i == current_idx:
                st.info(f"👉 Currently Crafting: {section['label']}")
            else:
                st.caption(f"⚪ Pending: {section['label']}")
        
        st.write("---")
        # COMMIT GATE
        if st.button(f"🔥 Commit & Advance to Section {current_idx + 2}" if current_idx < 5 else "🔥 Finalize Master Guide", use_container_width=True):
            # Save progress to database
            save_brand_data(user_id, st.session_state.final_soul_guide_parts[section_key], chamber=f"guide_part_{section_key}")
            
            # If it's the final section, compile the full guide
            if current_idx == 5:
                full_guide = "\n\n".join([st.session_state.final_soul_guide_parts[s["id"]] for s in guide_sections])
                save_brand_data(user_id, full_guide, chamber="soul_guide")
            
            st.session_state.guide_step_idx += 1
            st.success("Section locked. Moving forward...")
            time.sleep(1)
            st.rerun()