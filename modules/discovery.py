import streamlit as st
import time

try:
    from utils.gemini_ai import get_soul_rebel_consultant
    from utils.supabase_db import save_brand_data, load_brand_data
except Exception as e:
    st.error(f"Error loading backend modules: {e}")

def run(user_id):
    # 1. Load existing data from Supabase
    if "brand_soul" not in st.session_state:
        saved_data = load_brand_data(user_id)
        st.session_state.brand_soul = saved_data if saved_data else {}
    
    # 2. Initialize History & State
    if "chamber_history" not in st.session_state:
        st.session_state.chamber_history = {
            "purpus_summary": [], "brand_identity": [], 
            "brand_experience": [], "brand_impact": []
        }
    
    if "is_synthesizing" not in st.session_state:
        st.session_state.is_synthesizing = False
    
    # 3. Chamber Mapping & Opening Inquiries
    chamber_map = {
        "✨ Chamber 1: PurpUS": "purpus_summary",
        "🎭 Chamber 2: Brand Identity": "brand_identity",
        "🌟 Chamber 3: Brand Experience": "brand_experience",
        "🌍 Chamber 4: Brand Impact": "brand_impact"
    }

    chamber_prompts = {
        "purpus_summary": "We are entering the Nucleus. Forget what you sell—Why must this brand exist in a world that already has enough noise? What is the 'internal fire' that fuels you?",
        "brand_identity": "Let's define the Individual. If your brand walked into a room, what is the 'vibe' it projects? Describe its unique fingerprint and persona.",
        "brand_experience": "How does a person *feel* the moment they touch your brand? Describe the ritual of engagement—how do you turn a customer into a believer?",
        "brand_impact": "The Legacy. Fifty years from now, what is the social footprint this Individual leaves behind? How has the world changed because of your work?"
    }

    col1, col2 = st.columns([3, 2])

    with col1:
        st.title("🔥 The Soul Sprint")
        
        # --- PROACTIVE CHAMBER SELECTOR ---
        selected_label = st.selectbox(
            "Current Extraction Focus:",
            options=list(chamber_map.keys()),
            index=0
        )
        new_target = chamber_map[selected_label]

        if "messages" not in st.session_state:
            st.session_state.messages = []

        # TRIGGER: Switch chamber and add the opening inquiry if not already present
        if st.session_state.get("target_chamber") != new_target:
            st.session_state.target_chamber = new_target
            chamber_has_messages = any(m.get("chamber") == new_target for m in st.session_state.messages)
            if not chamber_has_messages:
                opening_q = chamber_prompts[new_target]
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": opening_q, 
                    "chamber": new_target
                })
            st.rerun()

        # --- FILTERED CHAT DISPLAY ---
        active_messages = [m for m in st.session_state.messages if m.get("chamber") == new_target]

        for i, message in enumerate(active_messages):
            if i == 0 and len(active_messages) > 3:
                continue
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # --- INPUT ---
        st.write("---")
        audio_input = st.audio_input("🎤 Speak your truth", key="soul_audio_recorder")
        prompt = st.chat_input("Or type your thoughts...")

        new_input = None
        if audio_input:
            audio_id = hash(f"{audio_input.name}_{audio_input.size}")
            if st.session_state.get("last_audio_id") != audio_id:
                new_input = audio_input 
                st.session_state.last_audio_id = audio_id
        elif prompt:
            new_input = prompt

        if new_input:
            st.session_state.is_synthesizing = True
            display_text = "🎤 *Voice Memo Submitted*" if audio_input else prompt
            st.session_state.messages.append({"role": "user", "content": display_text, "chamber": new_target})
            
            context = "\n".join([f"{m['role']}: {m['content']}" for m in active_messages])
            
            with st.chat_message("assistant"):
                with st.spinner(f"Synthesizing Strategy for {selected_label}..."):
                    strategic_instruction = (
                        f"\n\n--- INSTRUCTION ---\n"
                        f"1. Provide a warm conversational reflection.\n"
                        f"2. Provide the formal strategy for {selected_label} wrapped in [STRATEGY] and [/STRATEGY] tags.\n"
                        f"3. EVALUATE: If the strategy feels complete, invite the user to move to the next chamber. "
                        f"If it needs more depth, ask one targeted follow-up question."
                    )
                    
                    full_response = get_soul_rebel_consultant(new_input, context + strategic_instruction)
                    
                    if "[STRATEGY]" in full_response:
                        parts = full_response.split("[STRATEGY]")
                        chat_part = parts[0].strip()
                        strategy_part = parts[1].split("[/STRATEGY]")[0].strip() if "[/STRATEGY]" in parts[1] else parts[1].strip()
                    else:
                        chat_part = full_response
                        strategy_part = full_response

                    st.markdown(chat_part)
                    st.session_state.messages.append({"role": "assistant", "content": chat_part, "chamber": new_target})
                    
                    target_col = st.session_state.target_chamber
                    save_brand_data(user_id, strategy_part, chamber=target_col)
                    st.session_state.brand_soul[target_col] = strategy_part
                    st.session_state.is_synthesizing = False
            st.rerun() 

    with col2:
        st.subheader("👤 Brand Individual: Vital Signs")
        brand_data = st.session_state.get('brand_soul', {})
        
        filled = sum(1 for k in chamber_map.values() if brand_data.get(k))
        progress = filled / 4

        if st.session_state.is_synthesizing:
            st.info("💓 **Status: Soul Extraction in Progress**")
        else:
            st.write(f"**Soul Alignment:** {int(progress * 100)}%")
            st.progress(progress)

        st.write("---")
        st.subheader("📋 Strategy Chambers")
        
        edit_mode = st.toggle("🛠️ Enable Manual Edit Mode")

        for label, key in chamber_map.items():
            is_expanded = (st.session_state.target_chamber == key)
            with st.expander(label, expanded=is_expanded):
                current_content = brand_data.get(key, "")

                if edit_mode:
                    # Version History
                    history = st.session_state.chamber_history.get(key, [])
                    if history:
                        with st.popover("🕒 Version History"):
                            for idx, old_ver in enumerate(reversed(history)):
                                if st.button(f"Restore v{len(history)-idx}", key=f"rev_{key}_{idx}"):
                                    st.session_state.brand_soul[key] = old_ver
                                    save_brand_data(user_id, old_ver, chamber=key)
                                    st.rerun()

                    # Editing UI - Using 'value' to bind to state safely
                    new_content = st.text_area(
                        f"Refine {label}:", 
                        value=current_content, 
                        height=200, 
                        key=f"widget_{key}"
                    )
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button(f"💾 Update {label}", key=f"save_{key}"):
                            st.session_state.brand_soul[key] = new_content
                            if current_content:
                                st.session_state.chamber_history[key].append(current_content)
                            save_brand_data(user_id, new_content, chamber=key)
                            st.success("Updated.")
                            time.sleep(0.5)
                            st.rerun()
                    with c2:
                        if st.button(f"🗑️ Clear {label}", key=f"delete_{key}"):
                            # We reset the source of truth; the 'value' param above handles the UI wipe
                            st.session_state.brand_soul[key] = ""
                            save_brand_data(user_id, "", chamber=key)
                            st.warning(f"{label} Cleared.")
                            time.sleep(0.4)
                            st.rerun()
                else:
                    if current_content:
                        st.markdown(current_content)
                    else:
                        st.caption("Awaiting discovery...")