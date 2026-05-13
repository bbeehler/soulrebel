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

    col1, col2 = st.columns([3, 2])

    with col1:
        st.title("🔥 The Soul Sprint")
        st.write("Extracting the essence of your brand Individual.")
        
        # Chat History
        if "messages" not in st.session_state:
            st.session_state.messages = [{"role": "assistant", "content": "The Soul Rebel Consultant is active. Tell me, what is the core 'Why' that keeps your brand's soul burning?"}]

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
            
            context = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
            
            with st.chat_message("assistant"):
                with st.spinner("Synthesizing your Persona..."):
                    response = get_soul_rebel_consultant(new_input, context)
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    
                    save_brand_data(user_id, response)
                    st.session_state.brand_soul['purpus_summary'] = response
                    st.session_state.is_synthesizing = False
            
            st.rerun() 

    with col2:
        # --- THE INDIVIDUAL PERSONA MONITOR ---
        st.subheader("👤 Brand Individual: Vital Signs")
        
        # Pull current data
        brand_data = st.session_state.get('brand_soul', {})
        
        # Logic for the "Heartbeat" of the Individual
        if st.session_state.is_synthesizing:
            st.info("💓 **Status: Soul Extraction in Progress**")
            st.caption("The Individual is evolving. Gemini is listening to your tone and conviction.")
        else:
            # Simple progress logic: how many chambers are filled?
            chambers_filled = sum(1 for k in ['purpus_summary', 'brand_identity', 'brand_experience', 'brand_impact'] if brand_data.get(k))
            completion_pct = (chambers_filled / 4)
            
            st.write(f"**Soul Alignment:** {int(completion_pct * 100)}%")
            st.progress(completion_pct)
            
            if chambers_filled == 0:
                st.warning("Status: Latent. (Awaiting first extraction)")
            elif chambers_filled < 4:
                st.success("Status: Awakening.")
            else:
                st.balloons()
                st.success("Status: Fully Realized Individual.")

        st.write("---")
        st.subheader("📋 Strategy Chambers")
        
        with st.expander("✨ Chamber 1: PurpUS", expanded=True):
            if st.session_state.is_synthesizing:
                st.warning("⚡ Synthesizing 'The Soul'...")
            else:
                st.write(brand_data.get('purpus_summary', "Awaiting deeper discovery..."))
            
        with st.expander("🎭 Chamber 2: Brand Identity"):
            st.write(brand_data.get('brand_identity', "Defining your Soul Rebel persona..."))

        with st.expander("🌟 Chamber 3: Brand Experience"):
            st.write(brand_data.get('brand_experience', "Mapping the customer journey..."))

        with st.expander("🌍 Chamber 4: Brand Impact"):
            st.write(brand_data.get('brand_impact', "Defining your legacy..."))