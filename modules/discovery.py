import streamlit as st
import time

try:
    from utils.gemini_ai import get_soul_rebel_consultant
    from utils.supabase_db import save_brand_data, load_brand_data
except Exception as e:
    st.error(f"Error loading backend modules: {e}")

def run(user_id):
    # 1. Sync State with Database
    if "brand_soul" not in st.session_state:
        saved_data = load_brand_data(user_id)
        st.session_state.brand_soul = saved_data if saved_data else {}
    
    if "widget_seeds" not in st.session_state:
        st.session_state.widget_seeds = {k: 0 for k in ["purpus_summary", "brand_identity", "brand_experience", "brand_impact"]}
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    chamber_map = {
        "✨ Soul (PurpUS)": "purpus_summary",
        "🎭 Mind (Identity)": "brand_identity",
        "🌟 Body (Experience)": "brand_experience",
        "🌍 Body (Impact)": "brand_impact"
    }
    chamber_sequence = ["purpus_summary", "brand_identity", "brand_experience", "brand_impact"]
    
    col1, col2 = st.columns([3, 2])

    with col1:
        st.title("🔥 The Soul Audit")
        st.caption("Determining who you are and defining your daily impact. [cite: 50, 52]")
        
        # Navigation
        current_chamber_key = st.session_state.get("target_chamber", "purpus_summary")
        chamber_keys = list(chamber_map.values())
        current_idx = chamber_keys.index(current_chamber_key) if current_chamber_key in chamber_keys else 0

        selected_label = st.selectbox("Current Audit Focus:", options=list(chamber_map.keys()), index=current_idx)
        new_target = chamber_map[selected_label]

        if st.session_state.get("target_chamber") != new_target:
            st.session_state.target_chamber = new_target
            st.rerun()

        # Initial Prompt per Chamber
        chamber_prompts = {
            "purpus_summary": "Foundation Phase: Why MUST this brand exist? What internal fire drives this soul? [cite: 36, 53]",
            "brand_identity": "The Foundation: If this brand were an individual, what is its identity and ethos? [cite: 41, 54]",
            "brand_experience": "Remarkable Experiences: How will your brand communicate its value while putting your audience first? [cite: 43]",
            "brand_impact": "The Legacy: What urgent community problems are you solving to create ongoing impact? [cite: 70, 80]"
        }
        if not any(m.get("chamber") == new_target for m in st.session_state.messages):
            st.session_state.messages.append({"role": "assistant", "content": chamber_prompts[new_target], "chamber": new_target})

        # Chat display
        for message in [m for m in st.session_state.messages if m.get("chamber") == new_target]:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Input handling
        st.write("---")
        prompt = st.chat_input("Document your thoughts...")

        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt, "chamber": new_target})
            with st.chat_message("assistant"):
                with st.spinner("Unearthing deeper alignment..."):
                    
                    next_idx = current_idx + 1
                    next_key = chamber_sequence[next_idx] if next_idx < len(chamber_sequence) else "COMPLETE"
                    
                    # MANDATORY GATEKEEPING INSTRUCTIONS
                    methodology = f"""
                    SYSTEM CONTEXT: You are the Godzspeed Soul Rebel Facilitator. [cite: 36]
                    
                    HARD RULES FOR PROGRESSION:
                    1. BUILD CONTENT: Always synthesize the user's input and provide a formal summary inside [STRATEGY]...[/STRATEGY] tags.
                    2. FACILITATE, DON'T FORCE: If the vision is solidified, ask: 'I feel we have unearthed the soul of this section. Are you ready to move forward to the next phase, or is there more to unearth here?'
                    3. TRIGGER MOVE: ONLY use the tag [MOVE_TO_CHAMBER:{next_key}] if the user explicitly confirms they are ready to move. 
                    4. APPEND: Your strategic summaries must be additive. 
                    
                    The success of this work hinges on getting to the deepest place possible. 
                    """
                    
                    current_context = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages if m.get("chamber") == new_target])
                    full_response = get_soul_rebel_consultant(prompt, methodology + current_context)

                    # Extract strategy data and navigation
                    strategy_part = ""
                    if "[STRATEGY]" in full_response:
                        parts = full_response.split("[STRATEGY]")
                        chat_part = parts[0].strip()
                        strategy_part = parts[1].split("[/STRATEGY]")[0].strip() if "[/STRATEGY]" in parts[1] else parts[1].strip()
                    else:
                        chat_part = full_response

                    if "[MOVE_TO_CHAMBER:" in chat_part:
                        move_tag = chat_part.split("[MOVE_TO_CHAMBER:")[1].split("]")[0]
                        chat_part = chat_part.split("[MOVE_TO_CHAMBER:")[0].strip()
                        if move_tag != "COMPLETE":
                            st.session_state.target_chamber = move_tag

                    # Update State and Sync Database
                    st.session_state.messages.append({"role": "assistant", "content": chat_part, "chamber": new_target})
                    
                    if strategy_part:
                        existing = st.session_state.brand_soul.get(new_target, "")
                        combined = f"{existing}\n\n{strategy_part}".strip()
                        st.session_state.brand_soul[new_target] = combined
                        save_brand_data(user_id, combined, chamber=new_target)
                    
                    st.rerun()

    with col2:
        st.subheader("🧬 Foundation Progress")
        # Ensure col2 pulls from the most recent session state
        brand_data = st.session_state.brand_soul
        filled = sum(1 for k in chamber_sequence if brand_data.get(k))
        st.progress(filled/4)

        st.write("---")
        st.subheader("📋 Documented Vision")
        for label, key in chamber_map.items():
            with st.expander(label, expanded=(current_chamber_key == key)):
                content = brand_data.get(key, "")
                if content:
                    st.markdown(content)
                else:
                    st.caption("Awaiting deeper unearthing... ")