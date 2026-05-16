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

    # The 12-step hierarchy based on the provided benchmark [cite: 1, 2]
    guide_structure = [
        {"id": "identity_big_idea", "label": "SECTION 1: IDENTITY", "sub": "Big Idea", "prompt": "Create a rousing affirmation that ignites creativity[cite: 5, 14]."},
        {"id": "identity_meaning", "label": "SECTION 1: IDENTITY", "sub": "What It Means", "prompt": "Deep narrative explaining the 'why' and the community impact[cite: 7, 8, 24]."},
        {"id": "identity_vision", "label": "SECTION 1: IDENTITY", "sub": "Vision & Mission", "prompt": "Radical transformation and bold reimagining of the future[cite: 28, 55, 56]."},
        {"id": "process_method", "label": "SECTION 2: PROCESS", "sub": "Transformation Process", "prompt": "Detail the 3-way radical methodology (e.g., Blueprint, Advocate, Inform)[cite: 72, 73, 74, 75]."},
        {"id": "anchors_culture", "label": "SECTION 3: ANCHORS", "sub": "Our Culture & Values", "prompt": "Define core soul pillars such as Humility, Diversity, and Curiosity[cite: 103, 107]."},
        {"id": "anchors_beliefs", "label": "SECTION 3: ANCHORS", "sub": "Beliefs & Behaviours", "prompt": "Draft 'We Believe' and 'We Always' statements that guide daily precision[cite: 158, 172]."},
        {"id": "positioning_1soul", "label": "SECTION 4: POSITIONING", "sub": "1Soul Statement", "prompt": "The authoritative statement demystifying and resolving complex problems[cite: 183, 193]."},
        {"id": "positioning_offering", "label": "SECTION 4: POSITIONING", "sub": "Our Offering", "prompt": "Tailored value propositions for Staff, Clients, and Communities[cite: 197, 198, 210, 223]."},
        {"id": "positioning_audience", "label": "SECTION 4: POSITIONING", "sub": "Target Audience", "prompt": "Detailed profiles of 'Allies' and 'Target Partners'[cite: 246, 247, 264]."},
        {"id": "expression_voice", "label": "SECTION 5: EXPRESSION", "sub": "Voice & Personality", "prompt": "Human, compelling, hella smart; The Caring Catalyst archetypes[cite: 326, 332]."},
        {"id": "ties_legacy", "label": "SECTION 6: SOUL TIES", "sub": "Brand Legacy", "prompt": "The 'living legacy' intended for lifetimes to come[cite: 343, 345]."},
        {"id": "ties_markers", "label": "SECTION 6: SOUL TIES", "sub": "Key Soul Markers (KPIs)", "prompt": "Strategic metrics framed as 'Do I/Am I' audit questions[cite: 357, 364]."}
    ]

    if "guide_idx" not in st.session_state:
        st.session_state.guide_idx = 0
    if "guide_content" not in st.session_state:
        st.session_state.guide_content = brand_data.get("soul_guide_parts", {})

    curr_idx = st.session_state.guide_idx

    # --- COMPLETION VIEW ---
    if curr_idx >= len(guide_structure):
        st.success("🎉 Master Soul Guide Complete.")
        full_text = "\n\n".join(st.session_state.guide_content.values())
        st.text_area("Full Strategic Individual Narrative", value=full_text, height=600)
        
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
        st.info(f"**Strategic Focus:** {curr_sub['sub']}")
        
        # A. INITIAL GENERATION (Seed from Audit)
        if sub_key not in st.session_state.guide_content:
            with st.spinner(f"Initial Synthesis of {curr_sub['sub']}..."):
                methodology = f"""
                ROLE: Godzspeed Soul Rebel Facilitator.
                TASK: Draft the '{curr_sub['sub']}' section.
                MAPPING: {curr_sub['prompt']}
                VOICE: Human, compelling, hella smart.
                GAP DETECTION: If the Audit data is insufficient for this specific section, append '🚨 FACILITATOR INQUIRY' at the bottom with 3 thought-provoking questions.
                """
                draft = get_soul_rebel_consultant(f"Draft {curr_sub['sub']}", methodology + str(brand_data))
                st.session_state.guide_content[sub_key] = draft
                # Initialize the widget key
                st.session_state[f"text_val_{sub_key}"] = draft

        # B. DYNAMIC TEXT AREA (The Adaptive Field)
        # Using a specific key to force the widget to refresh when the AI synthesizes new info.
        edited_text = st.text_area(
            "Refine and Expand Narrative:", 
            value=st.session_state.get(f"text_val_{sub_key}", st.session_state.guide_content[sub_key]), 
            height=450, 
            key=f"input_{sub_key}"
        )
        
        # Track manual edits in the session state
        st.session_state.guide_content[sub_key] = edited_text
        
        # C. COLLABORATIVE SYNTHESIS (The Chat Engine)
        st.write("---")
        user_input = st.chat_input(f"Feed more detail into {curr_sub['sub']}...")
        
        if user_input:
            with st.spinner("Synthesizing and adapting field..."):
                update_prompt = f"""
                You are an editor. UPDATE the following text with the NEW DETAIL provided by the user. 
                1. Braiding: Seamlessly integrate new info into the existing flow.
                2. Voice: Keep it human, compelling, and 'hella smart'.
                3. Cleanup: If the user's input answers a question from the '🚨 FACILITATOR INQUIRY', remove that question.
                4. Return ONLY the FULL updated narrative for the '{curr_sub['sub']}' section.
                
                EXISTING TEXT:
                {edited_text}
                """
                
                new_narrative = get_soul_rebel_consultant(user_input, update_prompt)
                
                # FORCE SYNC: Update both master sources
                st.session_state.guide_content[sub_key] = new_narrative
                st.session_state[f"text_val_{sub_key}"] = new_narrative
                
                # Force the UI to refresh with the new content
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
        
        # D. COMMIT GATE
        is_light = "🚨 FACILITATOR INQUIRY" in edited_text
        
        if is_light:
            st.error("Please address the Facilitator's questions above to reach the Gold Standard.")
            
        if st.button("🔥 Commit & Advance", use_container_width=True, disabled=is_light):
            # Persist this specific part to the DB
            save_brand_data(user_id, edited_text, chamber=f"guide_part_{sub_key}")
            
            # Move to next subsection
            st.session_state.guide_idx += 1
            st.rerun()