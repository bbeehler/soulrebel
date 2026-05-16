import streamlit as st
import time
from utils.gemini_ai import get_soul_rebel_consultant
from utils.supabase_db import save_brand_data, load_brand_data

def run(user_id):
    st.title("✨ Phase 03: Illumination")
    st.caption("Forging the Strategic Individual: Subsection by Subsection.")
    st.write("---")
    
    # 1. DATA INITIALIZATION
    db_data = load_brand_data(user_id)
    brand_data = db_data if db_data else {}

    # The 12-step hierarchy based on the Black Planning Project benchmark
    guide_structure = [
        {"id": "identity_big_idea", "label": "SECTION 1: IDENTITY", "sub": "Big Idea", "prompt": "Create a rousing affirmation."},
        {"id": "identity_meaning", "label": "SECTION 1: IDENTITY", "sub": "What It Means", "prompt": "Narrative explaining the 'why' behind the Big Idea."},
        {"id": "identity_vision", "label": "SECTION 1: IDENTITY", "sub": "Vision & Mission", "prompt": "Radical transformation and long-term goals[cite: 55, 56]."},
        {"id": "process_method", "label": "SECTION 2: PROCESS", "sub": "Transformation Process", "prompt": "Detail the 3-way radical transformation methodology[cite: 72]."},
        {"id": "anchors_culture", "label": "SECTION 3: ANCHORS", "sub": "Our Culture & Values", "prompt": "Define core soul pillars like Humility, Diversity, and Curiosity[cite: 107]."},
        {"id": "anchors_beliefs", "label": "SECTION 3: ANCHORS", "sub": "Beliefs & Behaviours", "prompt": "Draft 'We Believe' and 'We Always' statements."},
        {"id": "positioning_1soul", "label": "SECTION 4: POSITIONING", "sub": "1Soul Statement", "prompt": "The authoritative statement of purpose[cite: 183, 184]."},
        {"id": "positioning_offering", "label": "SECTION 4: POSITIONING", "sub": "Our Offering", "prompt": "Value propositions for Staff, Clients, and Communities[cite: 197]."},
        {"id": "positioning_audience", "label": "SECTION 4: POSITIONING", "sub": "Target Audience", "prompt": "Profiles for Allies and Target Partners[cite: 246]."},
        {"id": "expression_voice", "label": "SECTION 5: EXPRESSION", "sub": "Voice & Personality", "prompt": "Human, compelling, hella smart; The Caring Catalyst[cite: 326, 332]."},
        {"id": "ties_legacy", "label": "SECTION 6: SOUL TIES", "sub": "Brand Legacy", "prompt": "The 'living legacy' built over lifetimes[cite: 343, 345]."},
        {"id": "ties_markers", "label": "SECTION 6: SOUL TIES", "sub": "Key Soul Markers (KPIs)", "prompt": "'Do I/Am I' audit questions[cite: 357]."}
    ]

    if "guide_idx" not in st.session_state:
        st.session_state.guide_idx = 0
    if "guide_content" not in st.session_state:
        st.session_state.guide_content = brand_data.get("soul_guide_parts", {})

    curr_idx = st.session_state.guide_idx

    # COMPLETION VIEW
    if curr_idx >= len(guide_structure):
        st.success("🎉 Master Soul Guide Complete.")
        full_text = "\n\n".join(st.session_state.guide_content.values())
        st.text_area("Full Strategic Narrative", value=full_text, height=600)
        return

    curr_sub = guide_structure[curr_idx]
    sub_key = curr_sub["id"]

    # 2. WORKSPACE (LEFT COLUMN)
    col1, col2 = st.columns([3, 2])

    with col1:
        st.subheader(f"{curr_sub['label']}")
        st.info(f"**Current Subsection:** {curr_sub['sub']}")
        
        # Generation: Seed from Audit
        if sub_key not in st.session_state.guide_content:
            with st.spinner(f"Initial Synthesis of {curr_sub['sub']}..."):
                methodology = f"TASK: Draft the '{curr_sub['sub']}' section. MAPPING: {curr_sub['prompt']}. VOICE: Human, compelling, smart. GAP DETECTION: If audit info is missing, append '🚨 FACILITATOR INQUIRY'."
                draft = get_soul_rebel_consultant(f"Draft {curr_sub['sub']}", methodology + str(brand_data))
                st.session_state.guide_content[sub_key] = draft

        # THE DYNAMIC TEXT AREA
        current_draft_text = st.session_state.guide_content[sub_key]
        edited_text = st.text_area("Refine and Expand Narrative:", value=current_draft_text, height=450, key=f"input_{sub_key}")
        
        # Collaborative Chat
        st.write("---")
        user_input = st.chat_input(f"Feed more detail into {curr_sub['sub']}...")
        
        if user_input:
            with st.spinner("Synthesizing and adapting field..."):
                update_prompt = f"""
                You are an editor. UPDATE the following text with the NEW DETAIL. 
                1. Incorporate the new info into the existing flow.
                2. If the user answers a question from the '🚨 FACILITATOR INQUIRY', delete that question.
                3. Return ONLY the FULL updated narrative.
                
                EXISTING TEXT:
                {edited_text}
                """
                new_narrative = get_soul_rebel_consultant(user_input, update_prompt)
                st.session_state.guide_content[sub_key] = new_narrative
                st.rerun()

    # 3. ROADMAP (RIGHT COLUMN)
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
        # Commit Logic
        is_light = "🚨 FACILITATOR INQUIRY" in edited_text
        if is_light:
            st.error("Please address the Facilitator's questions above before committing.")
            
        if st.button("🔥 Commit & Advance", use_container_width=True, disabled=is_light):
            save_brand_data(user_id, edited_text, chamber=f"guide_part_{sub_key}")
            st.session_state.guide_idx += 1
            st.rerun()