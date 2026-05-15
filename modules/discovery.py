import streamlit as st
import time

try:
    from utils.gemini_ai import get_soul_rebel_consultant
    from utils.supabase_db import save_brand_data, load_brand_data
except Exception as e:
    st.error(f"Error loading backend modules: {e}")

def run(user_id):
    # 1. Initialize and Sync State with Database
    if "brand_soul" not in st.session_state:
        saved_data = load_brand_data(user_id)
        st.session_state.brand_soul = saved_data if saved_data else {}
    
    if "widget_seeds" not in st.session_state:
        st.session_state.widget_seeds = {k: 0 for k in ["purpus_summary", "brand_identity", "brand_experience", "brand_impact"]}
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    chamber_map = {
        "✨ Soul (PurpUS)": "purpus_summary",
        "🎭 Mind (Identity)": "brand_identity",
        "🌟 Body (Experience)": "brand_experience",
        "🌍 Body (Impact)": "brand_impact"
    }
    chamber_sequence = ["purpus_summary", "brand_identity", "brand_experience", "brand_impact"]
    
    col1, col2 = st.columns([3, 2])

    with col1:
        st.title("🔥 The Soul Audit")
        st.caption("Determining who you are and defining your daily impact.")
        
        # --- NAVIGATION LOGIC ---
        current_chamber_key = st.session_state.get("target_chamber", "purpus_summary")
        chamber_keys = list(chamber_map.values())
        current_idx = chamber_keys.index(current_chamber_key) if current_chamber_key in chamber_keys else 0

        selected_label = st.selectbox("Current Audit Focus:", options=list(chamber_map.keys()), index=current_idx)
        new_target = chamber_map[selected_label]

        if st.session_state.get("target_chamber") != new_target:
            st.session_state.target_chamber = new_target
            st.rerun()

        # Initial Chamber Prompts
        chamber_prompts = {
            "purpus_summary": "Foundation Phase: Why MUST this brand exist? What internal fire drives this soul?",
            "brand_identity": "The Foundation: If this brand were an individual, what is its identity and ethos?",
            "brand_experience": "Remarkable Experiences: How will your brand communicate its value while putting your audience first?",
            "brand_impact": "The Legacy: What urgent community problems are you solving to create ongoing impact?"
        }
        if not any(m.get("chamber") == new_target for m in st.session_state.messages):
            st.session_state.messages.append({"role": "assistant", "content": chamber_prompts[new_target], "chamber": new_target})

        # Chat display
        for message in [m for m in st.session_state.messages if m.get("chamber") == new_target]:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # --- INPUT HANDLING ---
        st.write("---")
        audio_input = st.audio_input("🎤 Speak your vision", key=f"audio_{new_target}")
        prompt = st.chat_input("Document your thoughts...")

        user_input_content = None
        if audio_input:
            audio_id = hash(f"{audio_input.name}_{audio_input.size}")
            if st.session_state.get("last_audio_id") != audio_id:
                user_input_content = "🎤 *Voice Memo Submitted*"
                st.session_state.last_audio_id = audio_id
        elif prompt:
            user_input_content = prompt

        if user_input_content:
            st.session_state.messages.append({"role": "user", "content": user_input_content, "chamber": new_target})
            with st.chat_message("assistant"):
                with st.spinner("Unearthing deeper alignment..."):
                    
                    next_idx = current_idx + 1
                    next_key = chamber_sequence[next_idx] if next_idx < len(chamber_sequence) else "COMPLETE"
                    
                    # UPDATED METHODOLOGY: Permission-based movement
                    methodology = f"""
                    SYSTEM CONTEXT: You are the Godzspeed Soul Rebel Facilitator.
                    
                    MANDATORY BEHAVIOR:
                    1. DATA CAPTURE: Wrap all strategic insights in [STRATEGY]...[/STRATEGY] tags.
                    2. PROGRESSION GATE: If the user is satisfied, YOU MUST ASK: "Are you ready to move to the next phase?" 
                    3. COMMAND: Only append [MOVE_TO_CHAMBER:{next_key}] IF the user explicitly says "Yes", "I'm ready", or "move forward".
                    4. STAY PUT: If the user is still answering questions, STAY in the current chamber.
                    5. APPEND: Always add to the existing vision.
                    
                    Current Chamber: {new_target}
                    """
                    
                    current_context = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages if m.get("chamber") == new_target])
                    full_response = get_soul_rebel_consultant(user_input_content, methodology + current_context)

                    # Extract strategy data
                    strategy_part = ""
                    if "[STRATEGY]" in full_response:
                        parts = full_response.split("[STRATEGY]")
                        chat_part = parts[0].strip()
                        strategy_part = parts[1].split("[/STRATEGY]")[0].strip() if "[/STRATEGY]" in parts[1] else parts[1].strip()
                    else:
                        chat_part = full_response

                    # Navigation Check - Only triggered by explicit command
                    target_move = None
                    if "[MOVE_TO_CHAMBER:" in chat_part:
                        target_move = chat_part.split("[MOVE_TO_CHAMBER:")[1].split("]")[0]
                        chat_part = chat_part.split("[MOVE_TO_CHAMBER:")[0].strip()

                    # 1. Update State & Database FIRST
                    if strategy_part:
                        existing = st.session_state.brand_soul.get(new_target, "")
                        combined = f"{existing}\n\n{strategy_part}".strip()
                        st.session_state.brand_soul[new_target] = combined
                        save_brand_data(user_id, combined, chamber=new_target)

                    # 2. Update Chat History
                    st.session_state.messages.append({"role": "assistant", "content": chat_part, "chamber": new_target})

                    # 3. Process navigation only after confirmation
                    if target_move and target_move != "COMPLETE":
                        # We only move if the user's latest input was a confirmation
                        confirm_words = ["yes", "ready", "forward", "good", "move", "comfortable"]
                        if any(word in user_input_content.lower() for word in confirm_words):
                            st.session_state.target_chamber = target_move
                    
                    st.rerun()

    with col2:
        st.subheader("🧬 Foundation Progress")
        # Pull directly from state to ensure the progress bar and expanders update instantly
        brand_data = st.session_state.brand_soul
        filled = sum(1 for k in chamber_sequence if brand_data.get(k))
        st.progress(filled/4)

        st.write("---")
        st.subheader("📋 Documented Vision")
        for label, key in chamber_map.items():
            with st.expander(label, expanded=(current_chamber_key == key)):
                content = brand_data.get(key, "")
                if content:
                    st.markdown(content)
                else:
                    st.caption("Awaiting deeper unearthing...")