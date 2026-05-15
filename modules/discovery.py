import streamlit as st
import time

try:
    from utils.gemini_ai import get_soul_rebel_consultant
    from utils.supabase_db import save_brand_data, load_brand_data
except Exception as e:
    st.error(f"Error loading backend modules: {e}")

def run(user_id):
    # 1. Initialize and Force Sync State
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
        st.caption("Unearthing the deepest possible understanding.")
        
        # --- NAVIGATION ---
        current_chamber_key = st.session_state.get("target_chamber", "purpus_summary")
        chamber_keys = list(chamber_map.values())
        current_idx = chamber_keys.index(current_chamber_key) if current_chamber_key in chamber_keys else 0

        selected_label = st.selectbox("Current Audit Focus:", options=list(chamber_map.keys()), index=current_idx)
        new_target = chamber_map[selected_label]

        if st.session_state.get("target_chamber") != new_target:
            st.session_state.target_chamber = new_target
            st.rerun()

        # Initial Prompts
        chamber_prompts = {
            "purpus_summary": "Foundation Phase: Why MUST this brand exist? What internal fire drives this soul?",
            "brand_identity": "The Foundation: If this brand were an individual, what is its identity and ethos?",
            "brand_experience": "Remarkable Experiences: How will your brand communicate its value while putting your audience first?",
            "brand_impact": "The Legacy: What urgent community problems are you solving to create ongoing impact?"
        }
        if not any(m.get("chamber") == new_target for m in st.session_state.messages):
            st.session_state.messages.append({"role": "assistant", "content": chamber_prompts[new_target], "chamber": new_target})

        # Chat display
        active_messages = [m for m in st.session_state.messages if m.get("chamber") == new_target]
        for message in active_messages:
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
                with st.spinner("Unearthing..."):
                    
                    next_idx = current_idx + 1
                    next_key = chamber_sequence[next_idx] if next_idx < len(chamber_sequence) else "COMPLETE"
                    
                    methodology = f"""
                    SYSTEM CONTEXT: You are a Godzspeed Facilitator. 
                    
                    HARD RULES:
                    1. CHALLENGE & PROBE: Do not be agreeable. Ask 'Why?' until the soul is unearthed.
                    2. DATA TAGGING: Wrap EVERY strategic insight or finalized summary in [STRATEGY]...[/STRATEGY] tags. 
                    3. THE GATE: When substance is found, ask: 'Are you ready to move to the next phase?'
                    4. COMMAND: Use [MOVE_TO_CHAMBER:{next_key}] ONLY if the user says 'Yes' or 'Ready'.
                    5. APPEND: New data must be ADDED to the document, not replace it.
                    """
                    
                    current_context = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages if m.get("chamber") == new_target])
                    full_response = get_soul_rebel_consultant(user_input_content, methodology + current_context)

                    # Extract Content
                    strategy_part = ""
                    if "[STRATEGY]" in full_response:
                        parts = full_response.split("[STRATEGY]")
                        chat_part = parts[0].strip()
                        strategy_part = parts[1].split("[/STRATEGY]")[0].strip() if "[/STRATEGY]" in parts[1] else parts[1].strip()
                    else:
                        chat_part = full_response

                    target_move = None
                    if "[MOVE_TO_CHAMBER:" in chat_part:
                        target_move = chat_part.split("[MOVE_TO_CHAMBER:")[1].split("]")[0]
                        chat_part = chat_part.split("[MOVE_TO_CHAMBER:")[0].strip()

                    # --- CRITICAL FIX: IMMEDIATE SYNC ---
                    if strategy_part:
                        existing = st.session_state.brand_soul.get(new_target, "")
                        combined = f"{existing}\n\n{strategy_part}".strip()
                        
                        # 1. Update Session State FIRST
                        st.session_state.brand_soul[new_target] = combined
                        # 2. Save to DB SECOND
                        save_brand_data(user_id, combined, chamber=new_target)

                    st.session_state.messages.append({"role": "assistant", "content": chat_part, "chamber": new_target})

                    if target_move and target_move != "COMPLETE":
                        confirm_words = ["yes", "ready", "forward", "good", "move", "comfortable", "proceed"]
                        if any(word in user_input_content.lower() for word in confirm_words):
                            st.session_state.target_chamber = target_move
                    
                    # Force a micro-pause to ensure DB commit
                    time.sleep(0.1)
                    st.rerun()

    with col2:
        st.subheader("🧬 Foundation Progress")
        # Pull directly from st.session_state to bypass any caching lag
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
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button(f"💾 Save {label}", key=f"save_{key}"):
                            st.session_state.brand_soul[key] = new_val
                            save_brand_data(user_id, new_val, chamber=key)
                            st.success("Updated.")
                            time.sleep(0.5)
                            st.rerun()
                    with c2:
                        if st.button(f"🗑️ Clear {label}", key=f"clear_{key}"):
                            st.session_state.brand_soul[key] = ""
                            save_brand_data(user_id, "", chamber=key)
                            st.session_state.messages = [m for m in st.session_state.messages if m.get("chamber") != key]
                            st.session_state.widget_seeds[key] += 1
                            st.rerun()
                else:
                    if content:
                        st.markdown(content)
                    else:
                        st.caption("Awaiting deeper unearthing...")