import streamlit as st
import time

try:
    from utils.gemini_ai import get_soul_rebel_consultant
    from utils.supabase_db import save_brand_data, load_brand_data
except Exception as e:
    st.error(f"Error loading backend modules: {e}")

def run(user_id):
    # 1. Initialize and Sync State
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
    
    # 2. UI Layout
    col1, col2 = st.columns([3, 2])

    with col1:
        st.title("🔥 The Soul Audit")
        st.caption("Identifying growth opportunities and defining your daily impact.")
        
        # Navigation
        current_chamber_key = st.session_state.get("target_chamber", "purpus_summary")
        chamber_keys = list(chamber_map.values())
        current_idx = chamber_keys.index(current_chamber_key) if current_chamber_key in chamber_keys else 0

        selected_label = st.selectbox("Current Audit Focus:", options=list(chamber_map.keys()), index=current_idx)
        new_target = chamber_map[selected_label]

        if st.session_state.get("target_chamber") != new_target:
            st.session_state.target_chamber = new_target
            st.rerun()

        # Opening Prompt
        chamber_prompts = {
            "purpus_summary": "Foundation Phase: Why MUST this brand exist? What internal fire drives this soul?",
            "brand_identity": "Designing the Individual: What are the core values and philosophies necessary to carry meaning?",
            "brand_experience": "Remarkable Experiences: How will your brand communicate its value while putting the audience first?",
            "brand_impact": "The Legacy: What urgent community problems are you solving to create ongoing impact?"
        }
        if not any(m.get("chamber") == new_target for m in st.session_state.messages):
            st.session_state.messages.append({"role": "assistant", "content": chamber_prompts[new_target], "chamber": new_target})

        # Chat History
        active_messages = [m for m in st.session_state.messages if m.get("chamber") == new_target]
        for message in active_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Input
        st.write("---")
        audio_input = st.audio_input("🎤 Speak your vision", key=f"audio_{new_target}")
        prompt = st.chat_input("Document your thoughts...")

        user_input = None
        if audio_input:
            audio_id = hash(f"{audio_input.name}_{audio_input.size}")
            if st.session_state.get("last_audio_id") != audio_id:
                user_input = "🎤 *Voice Vision Submitted*"
                st.session_state.last_audio_id = audio_id
        elif prompt:
            user_input = prompt

        # 3. AI Processing Logic
        if user_input:
            st.session_state.messages.append({"role": "user", "content": user_input, "chamber": new_target})
            
            with st.chat_message("assistant"):
                with st.spinner("Unearthing deeper alignment..."):
                    
                    next_idx = current_idx + 1
                    next_key = chamber_sequence[next_idx] if next_idx < len(chamber_sequence) else "COMPLETE"
                    
                    # TIGHT INSTRUCTIONS FOR FOLLOW-UP AND PROGRESSION
                    methodology = f"""
                    SYSTEM CONTEXT: You are the Godzspeed Soul Rebel Facilitator.
                    CURRENT PHASE: 02: Foundation.
                    CURRENT CHAMBER: {new_target}
                    
                    HARD RULES:
                    1. If the user's input is brief, ask a specific follow-up question to reach the 'deepest place possible'.
                    2. If the vision for THIS chamber is solidified, provide a strategic synthesis inside [STRATEGY] tags AND add [MOVE_TO_CHAMBER:{next_key}] at the end.
                    3. Do NOT move to the next chamber unless the current one has enough substance to build a 'Strategic Bible'.
                    4. Always maintain the CEO's tone: deep, tactful, and revolutionary.
                    """
                    
                    current_context = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages if m.get("chamber") == new_target])
                    full_response = get_soul_rebel_consultant(user_input, methodology + current_context)

                    # Data Extraction
                    strategy_part = ""
                    if "[STRATEGY]" in full_response:
                        parts = full_response.split("[STRATEGY]")
                        chat_part = parts[0].strip()
                        strategy_part = parts[1].split("[/STRATEGY]")[0].strip() if "[/STRATEGY]" in parts[1] else parts[1].strip()
                    else:
                        chat_part = full_response

                    # Navigation Logic
                    if "[MOVE_TO_CHAMBER:" in chat_part:
                        move_tag = chat_part.split("[MOVE_TO_CHAMBER:")[1].split("]")[0]
                        chat_part = chat_part.split("[MOVE_TO_CHAMBER:")[0].strip()
                        if move_tag != "COMPLETE":
                            st.session_state.target_chamber = move_tag

                    # Update Message State
                    st.session_state.messages.append({"role": "assistant", "content": chat_part, "chamber": new_target})
                    
                    # Update & Sync Vision Data
                    if strategy_part:
                        existing = st.session_state.brand_soul.get(new_target, "")
                        combined = f"{existing}\n\n{strategy_part}".strip()
                        # Update state immediately for UI refresh
                        st.session_state.brand_soul[new_target] = combined
                        save_brand_data(user_id, combined, chamber=new_target)
                    
                    st.rerun()

    with col2:
        st.subheader("🧬 Foundation Progress")
        brand_data = st.session_state.brand_soul
        filled = sum(1 for k in chamber_sequence if brand_data.get(k))
        st.progress(filled/4)

        st.write("---")
        st.subheader("📋 Documented Vision")
        edit_mode = st.toggle("🛠️ Edit Strategy Foundation")

        for label, key in chamber_map.items():
            is_expanded = (current_chamber_key == key)
            with st.expander(label, expanded=is_expanded):
                content = brand_data.get(key, "")
                if edit_mode:
                    dk = f"widget_{key}_{st.session_state.widget_seeds[key]}"
                    new_val = st.text_area(f"Refine {label}:", value=content, height=200, key=dk)
                    if st.button(f"💾 Save {label}", key=f"s_{key}"):
                        st.session_state.brand_soul[key] = new_val
                        save_brand_data(user_id, new_val, chamber=key)
                        st.success("Updated.")
                        st.rerun()
                else:
                    st.markdown(content if content else "*Awaiting deeper unearthing...*")