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
    
    # 2. State Management for the "Individual"
    if "is_synthesizing" not in st.session_state:
        st.session_state.is_synthesizing = False
    
    # 3. Track the target chamber for the current sprint
    if "target_chamber" not in st.session_state:
        st.session_state.target_chamber = "purpus_summary"

    col1, col2 = st.columns([3, 2])

    with col1:
        st.title("🔥 The Soul Sprint")
        st.write("Extracting the essence of your brand Individual.")
        
        # --- CHAMBER SELECTOR ---
        # This tells the system where to store the upcoming synthesis
        chamber_map = {
            "✨ Chamber 1: PurpUS": "purpus_summary",
            "🎭 Chamber 2: Brand Identity": "brand_identity",
            "🌟 Chamber 3: Brand Experience": "brand_experience",
            "🌍 Chamber 4: Brand Impact": "brand_impact"
        }
        
        selected_label = st.selectbox(
            "Which part of the Individual are we unearthing?",
            options=list(chamber_map.keys()),
            index=0
        )
        st.session_state.target_chamber = chamber_map[selected_label]

        # Chat History
        if "messages" not in st.session_state:
            st.session_state.messages = [{"role": "assistant", "content": f"The Soul Rebel Consultant is active. We are focusing on {selected_label}. Tell me your thoughts."}]

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Multimodal Input
        st.write("---")
        audio_input = st.audio_input("🎤 Speak your truth", key="soul_audio_recorder")
        prompt = st.chat_input("Or type your thoughts...")

        new_input = None
        if audio_input:
            audio_id = hash(audio_input.getvalue())
            if st.session_state.get("last_audio_id") != audio_id:
                new_input = audio_input
                st.session_state.last_audio_id = audio_id
        elif prompt:
            new_input = prompt

        if new_input:
            st.session_state.is_synthesizing = True
            display_text = "🎤 *Voice Memo Submitted*" if audio_input else prompt
            st.session_state.messages.append({"role": "user", "content": display_text})
            
            # Context for Gemini
            context = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
            
            with st.chat_message("assistant"):
                with st.spinner(f"Synthesizing {selected_label}..."):
                    response = get_soul_rebel_consultant(new_input, context)
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    
                    # SAVE TO THE TARGETED CHAMBER
                    target_col = st.session_state.target_chamber
                    save_brand_data(user_id, response, chamber=target_col)
                    
                    # Update local state immediately so progress moves
                    st.session_state.brand_soul[target_col] = response
                    st.session_state.is_synthesizing = False
            
            st.rerun() 

    with col2:
        # --- THE INDIVIDUAL PERSONA MONITOR ---
        st.subheader("👤 Brand Individual: Vital Signs")
        
        # Pull current data
        brand_data = st.session_state.get('brand_soul', {})
        
        # Logic for progress
        chambers = ['purpus_summary', 'brand_identity', 'brand_experience', 'brand_impact']
        filled_count = sum(1 for k in chambers if brand_data.get(k))
        completion_pct = (filled_count / 4)
        
        # Heartbeat logic
        if st.session_state.is_synthesizing:
            st.info("💓 **Status: Soul Extraction in Progress**")
            st.caption(f"Analyzing tone and conviction for {selected_label}...")
        else:
            st.write(f"**Soul Alignment:** {int(completion_pct * 100)}%")
            st.progress(completion_pct)
            
            if filled_count == 0:
                st.warning("Status: Latent.")
            elif filled_count < 4:
                st.success("Status: Awakening.")
            else:
                st.balloons()
                st.success("Status: Fully Realized.")

        st.write("---")
        st.subheader("📋 Strategy Chambers")
        
        with st.expander("✨ Chamber 1: PurpUS", expanded=(st.session_state.target_chamber == "purpus_summary")):
            st.write(brand_data.get('purpus_summary', "Awaiting deeper discovery..."))
            
        with st.expander("🎭 Chamber 2: Brand Identity", expanded=(st.session_state.target_chamber == "brand_identity")):
            st.write(brand_data.get('brand_identity', "Defining your Soul Rebel persona..."))

        with st.expander("🌟 Chamber 3: Brand Experience", expanded=(st.session_state.target_chamber == "brand_experience")):
            st.write(brand_data.get('brand_experience', "Mapping the customer journey..."))

        with st.expander("🌍 Chamber 4: Brand Impact", expanded=(st.session_state.target_chamber == "brand_impact")):
            st.write(brand_data.get('brand_impact', "Defining your legacy..."))