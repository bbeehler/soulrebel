import streamlit as st
import time

try:
    from utils.gemini_ai import get_soul_rebel_consultant
    from utils.supabase_db import save_brand_data, load_brand_data
except Exception as e:
    st.error(f"Error loading backend modules: {e}")

def run(user_id):
    # 1. Load existing data
    if "brand_soul" not in st.session_state:
        saved_data = load_brand_data(user_id)
        st.session_state.brand_soul = saved_data if saved_data else {}
    
    if "chamber_history" not in st.session_state:
        st.session_state.chamber_history = {
            "purpus_summary": [], "brand_identity": [], 
            "brand_experience": [], "brand_impact": []
        }
    
    if "is_synthesizing" not in st.session_state:
        st.session_state.is_synthesizing = False
    
    chamber_map = {
        "✨ Chamber 1: PurpUS": "purpus_summary",
        "🎭 Chamber 2: Brand Identity": "brand_identity",
        "🌟 Chamber 3: Brand Experience": "brand_experience",
        "🌍 Chamber 4: Brand Impact": "brand_impact"
    }

    chamber_prompts = {
        "purpus_summary": "We are entering the Nucleus. Forget what you sell—Why must this brand exist? What is the 'internal fire' that fuels you?",
        "brand_identity": "Let's define the Individual. If your brand walked into a room, what is the 'vibe' it projects? Describe its unique persona.",
        "brand_experience": "How does a person *feel* the moment they touch your brand? Describe the ritual of engagement.",
        "brand_impact": "The Legacy. Fifty years from now, what is the social footprint this Individual leaves behind?"
    }

    col1, col2 = st.columns([3, 2])

    with col1:
        st.title("🔥 The Soul Sprint")
        
        selected_label = st.selectbox("Current Extraction Focus:", options=list(chamber_map.keys()), index=0)
        new_target = chamber_map[selected_label]

        if "messages" not in st.session_state:
            st.session_state.messages = []

        # TRIGGER: Switch chamber and add the opening inquiry if no thread exists for it
        if st.session_state.get("target_chamber") != new_target:
            st.session_state.target_chamber = new_target
            chamber_has_messages = any(m.get("chamber") == new_target for m in st.session_state.messages)
            if not chamber_has_messages:
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": chamber_prompts[new_target], 
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
                with st.spinner(f"Synthesizing Strategy..."):
                    strategic_instruction = (
                        f"\n\n--- INSTRUCTION ---\n"
                        f"1. Provide a warm reflection.\n"
                        f"2. Provide formal strategy wrapped in [STRATEGY] tags.\n"
                        f"3. Ask a follow-up or invite them to the next chamber."
                    )
                    full_response = get_soul_rebel_consultant(new_input, context + strategic_instruction)
                    
                    if "[STRATEGY]" in full_response:
                        parts = full_response.split("[STRATEGY]")
                        chat_part = parts[0].strip()
                        strategy_part = parts[1].split("[/STRATEGY]")[0].strip() if "[/STRATEGY]" in parts[1] else parts[1].strip()
                    else:
                        chat_part, strategy_part = full_response, full_response

                    st.markdown(chat_part)
                    st.session_state.messages.append({"role": "assistant", "content": chat_part, "chamber": new_target})
                    
                    save_brand_data(user_id, strategy_part, chamber=new_target)
                    st.session_state.brand_soul[new_target] = strategy_part
                    st.session_state.is_synthesizing = False
            st.rerun() 

    with col2:
        st.subheader("👤 Brand Individual: Vital Signs")
        brand_data = st.session_state.get('brand_soul', {})
        filled = sum(1 for k in chamber_map.values() if brand_data.get(k))
        st.write(f"**Soul Alignment:** {int((filled/4) * 100)}%")
        st.progress(filled/4)

        st.write("---")
        st.subheader("📋 Strategy Chambers")
        edit_mode = st.toggle("🛠️ Enable Manual Edit Mode")

        for label, key in chamber_map.items():
            is_expanded = (st.session_state.target_chamber == key)
            with st.expander(label, expanded=is_expanded):
                current_content = brand_data.get(key, "")

                if edit_mode:
                    new_content = st.text_area(f"Refine {label}:", value=current_content, height=200, key=f"widget_{key}")
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button(f"💾 Update {label}", key=f"save_{key}"):
                            st.session_state.brand_soul[key] = new_content
                            save_brand_data(user_id, new_content, chamber=key)
                            st.rerun()
                    with c2:
                        if st.button(f"🗑️ Clear {label}", key=f"delete_{key}"):
                            # 1. Clear the strategy
                            st.session_state.brand_soul[key] = ""
                            save_brand_data(user_id, "", chamber=key)
                            
                            # 2. CLEAR THE CHAT THREAD FOR THIS CHAMBER
                            st.session_state.messages = [m for m in st.session_state.messages if m.get("chamber") != key]
                            
                            st.warning(f"{label} & Thread Cleared.")
                            time.sleep(0.5)
                            st.rerun()
                else:
                    if current_content:
                        st.markdown(current_content)
                    else:
                        st.caption("Awaiting discovery...")