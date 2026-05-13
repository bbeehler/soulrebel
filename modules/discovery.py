import streamlit as st

try:
    from utils.gemini_ai import get_soul_rebel_consultant
    from utils.supabase_db import save_brand_data, load_brand_data
except Exception as e:
    st.error(f"Error loading backend modules: {e}")

def run(user_id):
    # 1. Load existing data from Supabase for the specific logged-in user
    if "brand_soul" not in st.session_state:
        saved_data = load_brand_data(user_id)
        st.session_state.brand_soul = saved_data if saved_data else {}

    # Layout: 2 Columns (Chat and Live Canvas)
    col1, col2 = st.columns([3, 2])

    with col1:
        st.title("🔥 The Soul Sprint")
        st.write("Extracting your brand's foundation through voice or text.")
        
        # --- CHAT HISTORY CONTAINER ---
        if "messages" not in st.session_state:
            st.session_state.messages = [
                {"role": "assistant", "content": "Welcome. I am your Soul Rebel Consultant. Let's begin. What is the fundamental 'Why' behind your business?"}
            ]

        # Display Chat History
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # --- MULTIMODAL INPUT SECTION ---
        st.write("---")
        
        # Audio Input with a unique key
        audio_input = st.audio_input("🎤 Answer verbally to capture your soul's tone", key="soul_audio_recorder")
        prompt = st.chat_input("Or type your thoughts here...")

        # LOGIC GATE: Prevent infinite loops by tracking processed audio IDs
        new_input = None
        
        if audio_input:
            # Create a unique fingerprint for the audio file
            audio_id = hash(audio_input.getvalue())
            if st.session_state.get("last_audio_id") != audio_id:
                new_input = audio_input
                st.session_state.last_audio_id = audio_id
        elif prompt:
            new_input = prompt

        # --- AI PROCESSING LOGIC ---
        if new_input:
            # Display user input in chat
            display_text = "🎤 *Voice Memo Submitted*" if audio_input else prompt
            st.chat_message("user").markdown(display_text)
            st.session_state.messages.append({"role": "user", "content": display_text})

            # Create context for Gemini
            context = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
            
            with st.chat_message("assistant"):
                with st.spinner("Soul Rebel is listening and synthesizing..."):
                    # Call Gemini 2.0 Flash (Multimodal)
                    response = get_soul_rebel_consultant(new_input, context)
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    
                    # SAVE TO SUPABASE (Persisting the synthesis)
                    save_brand_data(user_id, response)
                    
                    # Update local state so Canvas (Column 2) refreshes immediately
                    if not st.session_state.brand_soul:
                        st.session_state.brand_soul = {}
                    st.session_state.brand_soul['purpus_summary'] = response
            
            # Force a rerun to update the UI and lock in the audio ID
            st.rerun() 

    with col2:
        st.subheader("📋 Live Strategy Canvas")
        st.info("Insights stored in your Godzspeed Cloud:")
        
        # Pull data from the local session state (synced with Supabase)
        brand_data = st.session_state.get('brand_soul', {})
        
        with st.expander("✨ Chamber 1: PurpUS", expanded=True):
            st.write(brand_data.get('purpus_summary', "Awaiting deeper discovery..."))
            
        with st.expander("🎭 Chamber 2: Brand Identity"):
            st.write(brand_data.get('brand_identity', "Defining your Soul Rebel persona..."))

        with st.expander("🌟 Chamber 3: Brand Experience"):
            st.write(brand_data.get('brand_experience', "Mapping the customer journey..."))

        with st.expander("🌍 Chamber 4: Brand Impact"):
            st.write(brand_data.get('brand_impact', "Defining your legacy and global footprint..."))