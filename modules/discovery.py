import streamlit as st
try:
    from utils.gemini_ai import get_soul_rebel_consultant
except Exception as e:
    st.error(f"Error loading AI brain: {e}")

def run():
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
            st.rerun() # Refresh to update the Canvas on the right

    with col2:
        st.subheader("📋 Live Strategy Canvas")
        st.info("Insights gathered during this session:")
        
        # This section will eventually pull 'summary' data from Gemini
        with st.expander("✨ Chamber 1: PurpUS", expanded=True):
            st.write(st.session_state.get('purpus_summary', "Awaiting deeper discovery..."))
            
        with st.expander("🎭 Chamber 2: Brand Identity"):
            st.write("Defining your Soul Rebel persona...")

        with st.expander("🌟 Chamber 3: Brand Experience"):
            st.write("Mapping the customer journey...")