import streamlit as st
import time
from utils.gemini_ai import get_soul_rebel_consultant
from utils.supabase_db import save_brand_data, load_brand_data

def run(user_id):
    st.title("✨ Phase 03: Illumination")
    st.caption("Forging the Strategic Individual: Subsection by Subsection.")
    st.write("---")
    
    # 1. LOAD DATA & INITIALIZE STATE
    db_data = load_brand_data(user_id)
    brand_data = db_data if db_data else {}

    # Define the 12-step hierarchy based on the Gold Standard blueprint
    guide_structure = [
        {"id": "identity_big_idea", "label": "SECTION 1: IDENTITY", "sub": "Big Idea", "prompt": "Create a rousing affirmation that ignites creativity."},
        {"id": "identity_meaning", "label": "SECTION 1: IDENTITY", "sub": "What It Means", "prompt": "Deep narrative dive explaining the 'why' and the people-first approach."},
        {"id": "identity_vision", "label": "SECTION 1: IDENTITY", "sub": "Vision & Mission", "prompt": "Bold reimagining and radical transformation goals."},
        {"id": "process_method", "label": "SECTION 2: PROCESS", "sub": "Transformation Process", "prompt": "Detail the 3-step radical methodology (e.g., Blueprint, Advocate, Inform)."},
        {"id": "anchors_culture", "label": "SECTION 3: ANCHORS", "sub": "Our Culture & Values", "prompt": "Define the heart and soul through humility, diversity, and connection."},
        {"id": "anchors_beliefs", "label": "SECTION 3: ANCHORS", "sub": "Beliefs & Behaviours", "prompt": "Draft 'We Believe' and 'We Always' statements that guide precision."},
        {"id": "positioning_1soul", "label": "SECTION 4: POSITIONING", "sub": "1Soul Statement", "prompt": "The authoritative statement demystifying complex problems."},
        {"id": "positioning_offering", "label": "SECTION 4: POSITIONING", "sub": "Our Offering", "prompt": "Tailored value propositions for Staff, Clients, and Communities."},
        {"id": "positioning_audience", "label": "SECTION 4: POSITIONING", "sub": "Target Audience", "prompt": "Detailed profiles of 'Allies' (Clients/Partners)."},
        {"id": "expression_voice", "label": "SECTION 5: EXPRESSION", "sub": "Voice & Personality", "prompt": "Human, Compelling, Smart; The Caring Catalyst."},
        {"id": "ties_legacy", "label": "SECTION 6: SOUL TIES", "sub": "Brand Legacy", "prompt": "What the brand will be known for over several lifetimes."},
        {"id": "ties_markers", "label": "SECTION 6: SOUL TIES", "sub": "Key Soul Markers (KPIs)", "prompt": "'Do I/Am I' audit questions to ensure the soul remains intact."}
    ]

    if "guide_idx" not in st.session_state:
        st.session_state.guide_idx = 0
    if "guide_content" not in st.session_state:
        st.session_state.guide_content = brand_data.get("soul_guide_parts", {})

    curr_idx = st.session_state.guide_idx

    # 2. COMPLETION CHECK
    if curr_idx >= len(guide_structure):
        st.success("🎉 Master Soul Guide Complete.")
        full_text = "\n\n".join(st.session_state.guide_content.values())
        st.text_area("Full Strategic Narrative", value=full_text, height=600)
        if st.button("🗑️ Restart Illumination"):
            st.session_state.guide_idx = 0
            st.session_state.guide_content = {}
            st.rerun()
        return

    curr_sub = guide_structure[curr_idx]
    sub_key = curr_sub["id"]

    # 3. WORKSPACE
    col1, col2 = st.columns([3, 2])

    with col1:
        st.subheader(f"{curr_sub['label']}")
        st.info(f"**Focusing on:** {curr_sub['sub']}")
        
        # Initial Subsection Draft with Gap Detection
        if sub_key not in st.session_state.guide_content:
            with st.spinner(f"Synthesizing {curr_sub['sub']}..."):
                methodology = f"""
                ROLE: Godzspeed Soul Rebel Facilitator. 
                TASK: Write the '{curr_sub['sub']}' subsection based on the Gold Standard.
                MANDATE: If the Soul Audit discovery data is insufficient, DO NOT hallucinate. 
                Instead, draft a skeleton and append '🚨 FACILITATOR INQUIRY' with 3 thought-provoking questions.
                """
                draft = get_soul_rebel_consultant(f"Draft {curr_sub['sub']}", methodology + str(brand_data))
                st.session_state.guide_content[sub_key] = draft

        # The Workspace
        current_text = st.session_state.guide_content[sub_key]
        
        if "🚨 FACILITATOR INQUIRY" in current_text:
            st.warning("More depth required. See the inquiries below the workspace.")

        edited_text = st.text_area("Refine subsection narrative:", value=current_text, height=400, key=f"area_{sub_key}")
        st.session_state.guide_content[sub_key] = edited_text

        # 4. COLLABORATIVE SYNTHESIS (Thought-Provoking Questions)
        st.write("---")
        user_input = st.chat_input(f"Feed more detail into {curr_sub['sub']}...")
        if user_input:
            with st.spinner("Braiding details into narrative..."):
                update_prompt = f"""
                Update the {curr_sub['sub']} subsection. 
                Synthesize the user's answer into the narrative and remove the specific inquiry that was answered.
                """
                new_text = get_soul_rebel_consultant(user_input, update_prompt + "\n\nCURRENT TEXT:\n" + edited_text)
                st.session_state.guide_content[sub_key] = new_text
                st.rerun()

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
        # Ensure the user doesn't commit a section that still has active inquiries
        is_light = "🚨 FACILITATOR INQUIRY" in edited_text
        
        if is_light:
            st.error("Section incomplete. Please address the Facilitator's questions to reach the Gold Standard.")
        
        if st.button("🔥 Commit & Advance Subsection", use_container_width=True, disabled=is_light):
            save_brand_data(user_id, st.session_state.guide_content[sub_key], chamber=f"guide_part_{sub_key}")
            st.session_state.guide_idx += 1
            st.rerun()