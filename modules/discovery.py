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
    
    # 2. State Management for UI and Processing
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

        # Initialize messages if empty
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Trigger opening question if chamber changes or is new
        if st.session_state.get("target_chamber") != new_target:
            st.session_state.target_chamber = new_target
            opening_q = chamber_prompts[new_target]
            st.session_state.messages.append({"role": "assistant", "content": opening_q})
            st.rerun()

        # Display Chat History (Skipping the very first message once conversation flows)
        for i, message in enumerate(st.session_state.messages):
            if i == 0 and len(st.session_state.messages) > 3:
                continue
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # --- MULTIMODAL INPUT ---
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
            st.session_state.messages.append({"role": "user", "content": display_text})
            
            context = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
            
            with st.chat_message("assistant"):
                with st.spinner(f"Synthesizing Strategy for {selected_label}..."):
                    # Command ensures the output is formatted for extraction
                    strategic_instruction = (
                        f"\n\n--- INSTRUCTION ---\n"
                        f"1. Provide a warm conversational reflection.\n"
                        f"2. Provide the formal strategy for {selected_label} wrapped in [STRATEGY] tags.\n"
                        f"3. End with a question for the next step."
                    )
                    
                    full_response = get_soul_rebel_consultant(new_input, context + strategic_instruction)
                    
                    # Extraction Logic
                    if "[STRATEGY]" in full_response:
                        parts = full_response.split("[STRATEGY]")
                        chat_part = parts[0].strip()
                        strategy_part = parts[1].split("[/STRATEGY]")[0].strip() if "[/STRATEGY]" in parts[1] else parts[1].strip()
                    else:
                        chat_part = full_response
                        strategy_part = full_response

                    st.markdown(chat_part)
                    st.session_state.messages.append({"role": "assistant", "content": chat_part})
                    
                    # Persist Polished Result
                    target_col = st.session_state.target_chamber
                    save_brand_data(user_id, strategy_part, chamber=target_col)
                    st.session_state.brand_soul[target_col] = strategy_part
                    
                    st.session_state.is_synthesizing = False
            st.rerun() 

    with col2:
        st.subheader("👤 Brand Individual: Vital Signs")
        brand_data = st.session_state.get('brand_soul', {})
        
        # Calculate Progress
        chambers = list(chamber_map.values())
        filled = sum(1 for k in chambers if brand_data.get(k))
        progress = filled / 4

        if st.session_state.is_synthesizing:
            st.info("💓 **Status: Soul Extraction in Progress**")
        else:
            st.write(f"**Soul Alignment:** {int(progress * 100)}%")
            st.progress(progress)

        st.write("---")
        st.subheader("📋 Strategy Chambers")
        
        for label, key in chamber_map.items():
            is_expanded = (st.session_state.target_chamber == key)
            with st.expander(label, expanded=is_expanded):
                st.markdown(brand_data.get(key, "Awaiting deeper discovery..."))