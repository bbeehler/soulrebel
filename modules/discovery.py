import streamlit as st

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

    # Layout: 2 Columns
    col1, col2 = st.columns([3, 2])

    with col1:
        st.title("🔥 The Soul Sprint")
        st.write("Speak or type your brand's foundation...")
        
        # --- AUDIO INPUT SECTION ---
        # Allowing the user to answer questions verbally
        audio_input = st.audio_input("Record your answer (Voice Memo)")

        # Chat History Container
        if "messages" not in st.session_state:
            st.session_state.messages = [
                {"role": "assistant", "content": "Welcome. I am your Soul Rebel Consultant. Let's begin. What is the fundamental 'Why' behind your business?"}
            ]

        # Display Chat History
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # LOGIC: Handle either Audio or Text Input
        prompt = st.chat_input("Or enter your thoughts here...")
        
        # Determine if we have a new input to process
        new_input = None
        if audio_input:
            new_input = audio_input  # Passing the actual audio object to Gemini
        elif prompt:
            new_input = prompt

        if new_input:
            # Display user input in chat
            display_text = "🎤 *Audio Response Submitted*" if audio_input else prompt
            st.chat_message("user").markdown(display_text)
            st.session_state.messages.append({"role": "user", "content": display_text})

            # Create context for Gemini
            context = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
            
            with st.chat_message("assistant"):
                with st.spinner("Listening and Synthesizing..."):
                    # Gemini 2.0 Flash handles both text and audio natively
                    response = get_soul_rebel_consultant(new_input, context)
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    
                    # SAVE TO SUPABASE
                    save_brand_data(user_id, response)
                    
                    # Update local state for Column 2
                    if not st.session_state.brand_soul:
                        st.session_state.brand_soul = {}
                    st.session_state.brand_soul['purpus_summary'] = response
            
            st.rerun() 

    with col2:
        st.subheader("📋 Live Strategy Canvas")
        st.info("Insights stored in your Godzspeed Cloud:")
        
        brand_data = st.session_state.get('brand_soul', {})
        
        with st.expander("✨ Chamber 1: PurpUS", expanded=True):
            st.write(brand_data.get('purpus_summary', "Awaiting deeper discovery..."))
            
        with st.expander("🎭 Chamber 2: Brand Identity"):
            st.write(brand_data.get('brand_identity', "Defining your Soul Rebel persona..."))

        with st.expander("🌟 Chamber 3: Brand Experience"):
            st.write(brand_data.get('brand_experience', "Mapping the customer journey..."))

        with st.expander("🌍 Chamber 4: Brand Impact"):
            st.write(brand_data.get('brand_impact', "Defining your legacy and global footprint..."))