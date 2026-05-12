import streamlit as st
# Import the AI consultant function from your utils folder
try:
    from utils.gemini_ai import get_soul_rebel_consultant
except Exception as e:
    st.error(f"Error loading AI brain: {e}")

def run():
    st.title("🔥 The Soul Sprint")
    st.write("Ready to build your brand legacy.")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Welcome. I am your Soul Rebel Consultant. What is the fundamental 'Why' behind your business?"}
        ]

    # Show messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat Input
    if prompt := st.chat_input("Type here..."):
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Get response
        context = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
        
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = get_soul_rebel_consultant(prompt, context)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})