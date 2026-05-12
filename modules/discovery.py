import streamlit as st
from utils.gemini_ai import get_soul_rebel_consultant

def run():
    st.title("🔥 The Soul Sprint")
    st.markdown("### Chamber 1: Unearthing Your PurpUS")
    st.write("Let's extract the core foundation of your brand.")
    st.divider()

    # Create the chat history memory
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Welcome. I am your Soul Rebel Consultant. Let's begin the Godzspeed Vision Retreat. What is the fundamental 'Why' behind your business?"}
        ]

    # Show previous messages on the screen
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # The text box where you type
    if prompt := st.chat_input("Enter your thoughts here..."):
        
        # Show your message immediately
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Gather history so the AI remembers what was said
        context = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[:-1]])

        # Call Gemini and show the response
        with st.chat_message("assistant"):
            with st.spinner("Analyzing your PurpUS..."):
                response = get_soul_rebel_consultant(prompt, context)
                st.markdown(response)
                
        # Save AI response to memory
        st.session_state.messages.append({"role": "assistant", "content": response})