import streamlit as st
try:
    from utils.gemini_ai import get_soul_rebel_consultant
    from utils.supabase_db import save_brand_data, load_brand_data
except Exception as e:
    st.error(f"Error loading backend modules: {e}")

def run():
    # 1. Load existing data from Supabase for 'Brian' at the start
    if "brand_soul" not in st.session_state:
        saved_data = load_brand_data("Brian")
        st.session_state.brand_soul = saved_data if saved_data else {}

    # Layout: 2 Columns (60% Chat, 40% Live Canvas)
    col1, col2 = st.columns([3, 2])

    with col1:
        st.title("🔥 The Soul Sprint")
        st.write("Extracting your brand's foundation...")
        
        # Chat History Container
        if "messages" not in st.session_state:
            st.session_state.messages = [
                {"role": "assistant", "content": "Welcome. I am your Soul Rebel Consultant. Let's begin. What is the fundamental 'Why' behind your business?"}
            ]

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Chat Input
        if prompt := st.chat_input("Enter your thoughts..."):
            st.chat_message("user").markdown(prompt)
            st.session_state.messages.append({"role": "user", "content": prompt})

            context = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
            
            with st.chat_message("assistant"):
                with st.spinner("Synthesizing..."):
                    response = get_soul_rebel_consultant(prompt, context)
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    
                    # SAVE TO SUPABASE:
                    # We send the AI response to the PurpUS summary for now
                    save_brand_data("Brian", response)
                    
                    # Update local state so the Canvas refreshes immediately
                    st.session_state.brand_soul['purpus_summary'] = response
            
            st.rerun() 

    with col2:
        st.subheader("📋 Live Strategy Canvas")
        st.info("Insights stored in your Godzspeed Cloud:")
        
        # Pull data from the database state
        brand_data = st.session_state.get('brand_soul', {})
        
        with st.expander("✨ Chamber 1: PurpUS", expanded=True):
            purpus_text = brand_data.get('purpus_summary', "Awaiting deeper discovery...")
            st.write(purpus_text)
            
        with st.expander("🎭 Chamber 2: Brand Identity"):
            st.write(brand_data.get('brand_identity', "Defining your Soul Rebel persona..."))

        with st.expander("🌟 Chamber 3: Brand Experience"):
            st.write("Mapping the customer journey...")