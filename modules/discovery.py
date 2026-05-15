import streamlit as st
import time

try:
    from utils.gemini_ai import get_soul_rebel_consultant
    from utils.supabase_db import save_brand_data, load_brand_data
except Exception as e:
    st.error(f"Error loading backend modules: {e}")

def run(user_id):
    # 1. Initialize State
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
    
    chamber_prompts = {
        "purpus_summary": "Foundation Phase: We determine who you are. Forget what you sell—Why MUST this brand exist? What internal fire drives this soul? [cite: 36, 50, 51]",
        "brand_identity": "The Foundation: Developing a vision for your ethos. If this brand were an individual, what is its soul and identity? [cite: 53, 54]",
        "brand_experience": "Remarkable Experiences: In this foundation, how will your brand communicate its substance and value while putting your audience first? [cite: 41, 43]",
        "brand_impact": "The Legacy: What urgent community problems are you solving? How will you create ongoing impact and solve challenges for your audiences? [cite: 23, 70, 80]"
    }

    col1, col2 = st.columns([3, 2])

    with col1:
        st.title("🔥 The Soul Audit")
        st.caption("Phase 02: Foundation — Identifying growth opportunities and defining your daily impact. [cite: 51, 52]")
        
        current_chamber_key = st.session_state.get("target_chamber", "purpus_summary")
        chamber_labels = list(chamber_map.keys())
        chamber_keys = list(chamber_map.values())
        
        try:
            current_idx = chamber_keys.index(current_chamber_key)
        except ValueError:
            current_idx = 0

        selected_label = st.selectbox("Current Audit Focus:", options=chamber_labels, index=current_idx)
        new_target = chamber_map[selected_label]

        if st.session_state.get("target_chamber") != new_target:
            st.session_state.target_chamber = new_target
            st.rerun()

        if not any(m.get("chamber") == new_target for m in st.session_state.messages):
            st.session_state.messages.append({"role": "assistant", "content": chamber_prompts[new_target], "chamber": new_target})

        active_messages = [m for m in st.session_state.messages if m.get("chamber") == new_target]
        for i, message in enumerate(active_messages):
            if i == 0 and len(active_messages) > 3: continue
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Completion Check
        brand_data = st.session_state.get('brand_soul', {})
        if all(brand_data.get(k) for k in chamber_sequence):
            st.success("🎉 **Foundation Complete.** You've unearthed the soul.")
            if st.button("✨ Proceed to Soul Illumination", use_container_width=True):
                st.session_state.target_page = "2. ✨ The Soul Guide"
                st.rerun()

        # --- INPUT HANDLING (VOICE + TEXT) ---
        st.write("---")
        audio_input = st.audio_input("🎤 Speak your vision", key=f"audio_{new_target}")
        prompt = st.chat_input("Document your thoughts...")

        user_input_content = None
        if audio_input:
            audio_id = hash(f"{audio_input.name}_{audio_input.size}")
            if st.session_state.get("last_audio_id") != audio_id:
                user_input_content = "🎤 *Voice Vision Submitted*"
                st.session_state.last_audio_id = audio_id
        elif prompt:
            user_input_content = prompt

        if user_input_content:
            st.session_state.messages.append({"role": "user", "content": user_input_content, "chamber": new_target})
            with st.chat_message("assistant"):
                with st.spinner("Unearthing deeper alignment..."):
                    next_idx = chamber_sequence.index(new_target) + 1
                    next_chamber_key = chamber_sequence[next_idx] if next_idx < len(chamber_sequence) else "COMPLETE"
                    
                    methodology = """
                    SYSTEM CONTEXT: You are the Godzspeed Soul Rebel Facilitator. You are in Phase 02: Foundation. [cite: 50]
                    Your mission is to unearth, illuminate, and ignite purpose-driven brands. [cite: 36]
                    
                    STRICT RULES:
                    1. DEEPENING: If the user's answer is shallow or you need more detail, ask follow-up questions. 
                    2. PROGRESSION: ONLY include [MOVE_TO_CHAMBER:X] when you have reached the 'deepest place possible' and the vision is solidified. 
                    3. REINFORCEMENT: Place formal strategic documentation inside [STRATEGY] tags.
                    4. IDENTITY OVER PROFIT: Focus on fit, legacy, and community impact. [cite: 60, 69, 84]
                    """
                    
                    current_context = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages if m.get("chamber") == new_target])
                    full_response = get_soul_rebel_consultant(user_input_content, methodology + current_context)

                    # LOGIC: Split Strategy vs Chat
                    if "[STRATEGY]" in full_response:
                        parts = full_response.split("[STRATEGY]")
                        chat_part = parts[0].strip()
                        strategy_part = parts[1].split("[/STRATEGY]")[0].strip() if "[/STRATEGY]" in parts[1] else parts[1].strip()
                    else:
                        chat_part, strategy_part = full_response, ""

                    # LOGIC: Check for Move command
                    if "[MOVE_TO_CHAMBER:" in chat_part:
                        move_tag = chat_part.split("[MOVE_TO_CHAMBER:")[1].split("]")[0]
                        chat_part = chat_part.split("[MOVE_TO_CHAMBER:")[0].strip()
                        if move_tag != "COMPLETE":
                            st.session_state.target_chamber = move_tag

                    st.session_state.messages.append({"role": "assistant", "content": chat_part, "chamber": new_target})
                    
                    # LOGIC: Append new strategic data instead of replacing it
                    if strategy_part:
                        existing_data = st.session_state.brand_soul.get(new_target, "")
                        combined_data = f"{existing_data}\n\n{strategy_part}".strip()
                        st.session_state.brand_soul[new_target] = combined_data
                        save_brand_data(user_id, combined_data, chamber=new_target)
                    
                    st.rerun()

    with col2:
        st.subheader("🧬 Foundation Progress")
        filled = sum(1 for k in chamber_sequence if st.session_state.brand_soul.get(k))
        st.progress(filled/4)

        st.write("---")
        st.subheader("📋 Documented Vision")
        edit_mode = st.toggle("🛠️ Edit Strategy Foundation")

        for label, key in chamber_map.items():
            is_expanded = (current_chamber_key == key)
            with st.expander(label, expanded=is_expanded):
                content = st.session_state.brand_soul.get(key, "")
                if edit_mode:
                    dk = f"widget_{key}_{st.session_state.widget_seeds[key]}"
                    new_val = st.text_area(f"Refine {label}:", value=content, height=200, key=dk)
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button(f"💾 Save {label}", key=f"save_{key}"):
                            st.session_state.brand_soul[key] = new_val
                            save_brand_data(user_id, new_val, chamber=key)
                            st.success("Updated.")
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