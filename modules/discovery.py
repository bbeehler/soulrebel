import streamlit as st
import time

try:
    from utils.gemini_ai import get_soul_rebel_consultant
    from utils.supabase_db import save_brand_data, load_brand_data
except Exception as e:
    st.error(f"Error loading backend modules: {e}")

def run(user_id):
    # 1. Load data & Initialize State
    if "brand_soul" not in st.session_state:
        saved_data = load_brand_data(user_id)
        st.session_state.brand_soul = saved_data if saved_data else {}
    
    if "widget_seeds" not in st.session_state:
        st.session_state.widget_seeds = {k: 0 for k in ["purpus_summary", "brand_identity", "brand_experience", "brand_impact"]}
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    chamber_map = {
        "✨ Chamber 1: PurpUS": "purpus_summary",
        "🎭 Chamber 2: Brand Identity": "brand_identity",
        "🌟 Chamber 3: Brand Experience": "brand_experience",
        "🌍 Chamber 4: Brand Impact": "brand_impact"
    }
    
    chamber_sequence = ["purpus_summary", "brand_identity", "brand_experience", "brand_impact"]
    chamber_prompts = {
        "purpus_summary": "We are entering the Nucleus. Forget what you sell—Why must this brand exist? What is the 'internal fire' that fuels you?",
        "brand_identity": "Let's define the Individual. If your brand walked into a room, what is the 'vibe' it projects? Describe its unique persona.",
        "brand_experience": "How does a person *feel* the moment they touch your brand? Describe the ritual of engagement.",
        "brand_impact": "The Legacy. Fifty years from now, what is the social footprint this Individual leaves behind?"
    }

    col1, col2 = st.columns([3, 2])

    with col1:
        st.title("🔥 The Soul Sprint")
        
        # Track dropdown state
        current_chamber_key = st.session_state.get("target_chamber", "purpus_summary")
        chamber_keys = list(chamber_map.values())
        current_idx = chamber_keys.index(current_chamber_key) if current_chamber_key in chamber_keys else 0

        selected_label = st.selectbox("Current Extraction Focus:", options=list(chamber_map.keys()), index=current_idx)
        new_target = chamber_map[selected_label]

        # Sync target chamber
        if st.session_state.get("target_chamber") != new_target:
            st.session_state.target_chamber = new_target
            st.rerun()

        # Ensure the opening prompt exists
        chamber_has_messages = any(m.get("chamber") == new_target for m in st.session_state.messages)
        if not chamber_has_messages:
            st.session_state.messages.append({"role": "assistant", "content": chamber_prompts[new_target], "chamber": new_target})

        # Filtered Chat
        active_messages = [m for m in st.session_state.messages if m.get("chamber") == new_target]
        for i, message in enumerate(active_messages):
            if i == 0 and len(active_messages) > 3: continue
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # --- INPUT HANDLING ---
        st.write("---")
        audio_input = st.audio_input("🎤 Speak your truth", key="soul_audio_recorder")
        prompt = st.chat_input("Or type your thoughts...")

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
                with st.spinner("Synthesizing Strategy..."):
                    next_idx = chamber_sequence.index(new_target) + 1
                    next_chamber_key = chamber_sequence[next_idx] if next_idx < len(chamber_sequence) else "COMPLETE"
                    
                    instruction = (
                        f"Provide a reflection. Provide formal strategy inside [STRATEGY] tags. "
                        f"If complete, add [MOVE_TO_CHAMBER:{next_chamber_key}] at the end."
                    )
                    
                    current_context = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages if m.get("chamber") == new_target])
                    full_response = get_soul_rebel_consultant(user_input_content, current_context + f"\n\n{instruction}")

                    # --- CLEANING & PARSING ---
                    # 1. Extract Strategy
                    if "[STRATEGY]" in full_response:
                        parts = full_response.split("[STRATEGY]")
                        chat_part = parts[0].strip()
                        strategy_part = parts[1].split("[/STRATEGY]")[0].strip() if "[/STRATEGY]" in parts[1] else parts[1].strip()
                    else:
                        chat_part, strategy_part = full_response, full_response

                    # 2. Check for Move Command and Strip it from the chat view
                    if "[MOVE_TO_CHAMBER:" in chat_part:
                        move_tag = chat_part.split("[MOVE_TO_CHAMBER:")[1].split("]")[0]
                        chat_part = chat_part.split("[MOVE_TO_CHAMBER:")[0].strip()
                        if move_tag != "COMPLETE":
                            st.session_state.target_chamber = move_tag
                            st.session_state.messages.append({
                                "role": "assistant", 
                                "content": f"✅ **Chamber Complete.**\n\n{chamber_prompts[move_tag]}", 
                                "chamber": move_tag
                            })

                    # 3. Final sanitization (removes any accidental leftovers)
                    clean_chat = chat_part.replace("[STRATEGY]", "").replace("[/STRATEGY]", "").replace("[DOC]", "").replace("[/DOC]", "").strip()

                    st.session_state.messages.append({"role": "assistant", "content": clean_chat, "chamber": new_target})
                    st.session_state.brand_soul[new_target] = strategy_part
                    save_brand_data(user_id, strategy_part, chamber=new_target)

            st.rerun()

    with col2:
        st.subheader("👤 Brand Individual: Vital Signs")
        brand_data = st.session_state.get('brand_soul', {})
        filled = sum(1 for k in chamber_sequence if brand_data.get(k))
        st.progress(filled/4)

        st.write("---")
        st.subheader("📋 Strategy Chambers")
        edit_mode = st.toggle("🛠️ Enable Manual Edit Mode")

        for label, key in chamber_map.items():
            is_expanded = (st.session_state.get("target_chamber") == key)
            with st.expander(label, expanded=is_expanded):
                content = brand_data.get(key, "")
                if edit_mode:
                    dk = f"widget_{key}_{st.session_state.widget_seeds[key]}"
                    new_val = st.text_area(f"Refine {label}:", value=content, height=200, key=dk)
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button(f"💾 Update {label}", key=f"s_{key}"):
                            st.session_state.brand_soul[key] = new_val
                            save_brand_data(user_id, new_val, chamber=key)
                            st.rerun()
                    with c2:
                        if st.button(f"🗑️ Clear {label}", key=f"d_{key}"):
                            st.session_state.brand_soul[key] = ""
                            save_brand_data(user_id, "", chamber=key)
                            st.session_state.messages = [m for m in st.session_state.messages if m.get("chamber") != key]
                            st.session_state.widget_seeds[key] += 1
                            st.rerun()
                else:
                    st.markdown(content if content else "Awaiting discovery...")