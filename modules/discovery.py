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
    
    # 2. State Management
    if "is_synthesizing" not in st.session_state:
        st.session_state.is_synthesizing = False
    
    if "target_chamber" not in st.session_state:
        st.session_state.target_chamber = "purpus_summary"

    col1, col2 = st.columns([3, 2])

    with col1:
        st.title("🔥 The Soul Sprint")
        st.write("Extracting the essence of your brand Individual.")
        
        # --- CHAMBER SELECTOR ---
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

        # --- CHAT HISTORY LOGIC ---
        if "messages" not in st.session_state:
            st.session_state.messages = [{"role": "assistant", "content": f"The Soul Rebel Consultant is active. We are focusing on {selected_label}. Tell me your thoughts."}]

        # Only show the welcome message if the conversation hasn't really started yet
        for i, message in enumerate(st.session_state.messages):
            if i == 0 and len(st.session_state.messages) > 2:
                continue # Hides the initial "The Soul Rebel is active" prompt after first exchange
                
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
            
            # Build history context
            context = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
            
            with st.chat_message("assistant"):
                with st.spinner(f"Unearthing {selected_label}..."):
                    # We inject a hidden 'Strategic Command' to ensure the output is in-depth
                    strategic_instruction = f"\n\nCOMMAND: Based on this input, synthesize a formal, 3-paragraph strategic definition for the {selected_label} chamber. Use bold headers and professional branding terminology."
                    
                    response = get_soul_rebel_consultant(new_input, context + strategic_instruction)
                    
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    
                    # PERSIST RESULTS
                    target_col = st.session_state.target_chamber
                    save_brand_data(user_id, response, chamber=target_col)
                    st.session_state.brand_soul[target_col] = response
                    
                    st.session_state.is_synthesizing = False
            
            st.rerun() 

    with col2:
        # --- THE INDIVIDUAL PERSONA MONITOR ---
        st.subheader("👤 Brand Individual: Vital Signs")
        brand_data = st.session_state.get('brand_soul', {})
        
        chambers = ['purpus_summary', 'brand_identity', 'brand_experience', 'brand_impact']
        filled_count = sum(1 for k in chambers if brand_data.get(k))
        completion_pct = (filled_count / 4)
        
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
        
        for label, key in chamber_map.items():
            is_expanded = (st.session_state.target_chamber == key)
            with st.expander(label, expanded=is_expanded):
                # Displays the formal strategic outcome
                content = brand_data.get(key, "Awaiting deeper discovery...")
                st.markdown(content)