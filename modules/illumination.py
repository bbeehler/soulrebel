import streamlit as st
import time
from utils.gemini_ai import get_soul_rebel_consultant
from utils.supabase_db import save_brand_data, load_brand_data

def run(user_id):
    st.title("✨ Phase 03: Illumination")
    st.caption("Forging the Strategic Individual: Subsection by Subsection.")
    st.write("---")
    
    # 1. INITIALIZE MASTER STATE
    db_data = load_brand_data(user_id)
    brand_data = db_data if db_data else {}

    # Standardized 12-step hierarchy
    guide_structure = [
        {"id": "identity_big_idea", "label": "SECTION 1: IDENTITY", "sub": "Big Idea", "prompt": "Create a rousing affirmation."},
        {"id": "identity_meaning", "label": "SECTION 1: IDENTITY", "sub": "What It Means", "prompt": "Deep narrative explaining the 'why'."},
        {"id": "identity_vision", "label": "SECTION 1: IDENTITY", "sub": "Vision & Mission", "prompt": "Radical transformation and bold reimagining."},
        {"id": "process_method", "label": "SECTION 2: PROCESS", "sub": "Transformation Process", "prompt": "Detail the 3-step radical methodology."},
        {"id": "anchors_culture", "label": "SECTION 3: ANCHORS", "sub": "Our Culture & Values", "prompt": "Define core soul pillars."},
        {"id": "anchors_beliefs", "label": "SECTION 3: ANCHORS", "sub": "Beliefs & Behaviours", "prompt": "Draft 'We Believe' and 'We Always' statements."},
        {"id": "positioning_1soul", "label": "SECTION 4: POSITIONING", "sub": "1Soul Statement", "prompt": "Authoritative statement of purpose."},
        {"id": "positioning_offering", "label": "SECTION 4: POSITIONING", "sub": "Our Offering", "prompt": "Value for Staff, Clients, Communities."},
        {"id": "positioning_audience", "label": "SECTION 4: POSITIONING", "sub": "Target Audience", "prompt": "Profiles of Allies/Partners."},
        {"id": "expression_voice", "label": "SECTION 5: EXPRESSION", "sub": "Voice & Personality", "prompt": "Human, compelling, smart; Caring Catalyst."},
        {"id": "ties_legacy", "label": "SECTION 6: SOUL TIES", "sub": "Brand Legacy", "prompt": "Living legacy for lifetimes to come."},
        {"id": "ties_markers", "label": "SECTION 6: SOUL TIES", "sub": "Key Soul Markers (KPIs)", "prompt": "'Do I/Am I' audit questions."}
    ]

    if "guide_idx" not in st.session_state:
        st.session_state.guide_idx = 0
    if "guide_content" not in st.session_state:
        st.session_state.guide_content = brand_data.get("soul_guide_parts", {})
    if "rev" not in st.session_state:
        st.session_state.rev = 0  # UI Revision counter to force refresh

    curr_idx = st.session_state.guide_idx

    # COMPLETION CHECK
    if curr_idx >= len(guide_structure):
        st.success("🎉 Master Soul Guide Complete.")
        full_text = "\n\n".join(st.session_state.guide_content.values())
        st.text_area("Full Strategic Narrative", value=full_text, height=600)
        if st.button("🗑️ Reset Illumination"):
            st.session_state.guide_idx = 0
            st.session_state.guide_content = {}
            st.rerun()
        return

    curr_sub = guide_structure[curr_idx]
    sub_key = curr_sub["id"]

    # 2. WORKSPACE LAYOUT
    col1, col2 = st.columns([3, 2])

    with col1:
        st.subheader(f"{curr_sub['label']}")
        st.info(f"**Focus:** {curr_sub['sub']}")
        
        # Initial Draft Generation
        if sub_key not in st.session_state.guide_content:
            with st.spinner(f"Initial Synthesis of {curr_sub['sub']}..."):
                methodology = f"Draft the '{curr_sub['sub']}' section. Focus: {curr_sub['prompt']}. VOICE: Human, compelling, smart. If data is missing, append '🚨 FACILITATOR INQUIRY'."
                draft = get_soul_rebel_consultant(f"Draft {curr_sub['sub']}", methodology + str(brand_data))
                st.session_state.guide_content[sub_key] = draft

        # THE REFRESHABLE WORKSPACE CONTAINER
        # Adding st.session_state.rev to the key forces a total re-render
        workspace_key = f"input_{sub_key}_v{st.session_state.rev}"
        
        current_text = st.session_state.guide_content[sub_key]
        
        # This text area will now completely reset whenever st.session_state.rev increases
        edited_text = st.text_area(
            "Refine and Expand Narrative:", 
            value=current_text, 
            height=450, 
            key=workspace_key
        )
        
        # Sync manual edits
        st.session_state.guide_content[sub_key] = edited_text

        # Collaborative Synthesis Loop
        st.write("---")
        user_input = st.chat_input(f"Feed more detail into {curr_sub['sub']}...")
        
        if user_input:
            with st.spinner("Synthesizing..."):
                update_prompt = f"""
                UPDATE the '{curr_sub['sub']}' narrative with NEW DETAIL. 
                - Braid the info into the flow.
                - Remove answered questions from '🚨 FACILITATOR INQUIRY'.
                - Return FULL UPDATED NARRATIVE ONLY.
                
                CURRENT: {edited_text}
                """
                new_narrative = get_soul_rebel_consultant(user_input, update_prompt)
                
                # CRITICAL: Update state AND increment revision to force UI update
                st.session_state.guide_content[sub_key] = new_narrative
                st.session_state.rev += 1 
                st.rerun()

    # 3. ROADMAP (RIGHT SIDE)
    with col2:
        st.subheader("📋 Blueprint Roadmap")
        for i, item in enumerate(guide_structure):
            if i < curr_idx:
                st.write(f"✅ {item['sub']}")
            elif i == curr_idx:
                st.markdown(f"**👉 {item['sub']}**")
            else:
                st.caption(f"⚪ {item['sub']}")
        
        st.write("---")
        is_light = "🚨 FACILITATOR INQUIRY" in edited_text
        if is_light:
            st.error("Please address the Facilitator's questions to reach the Gold Standard.")
            
        if st.button("🔥 Commit & Advance", use_container_width=True, disabled=is_light):
            save_brand_data(user_id, edited_text, chamber=f"guide_part_{sub_key}")
            st.session_state.guide_idx += 1
            st.session_state.rev = 0 # Reset revision for next section
            st.rerun()