import streamlit as st
import time

try:
    from utils.gemini_ai import get_soul_rebel_consultant
    from utils.supabase_db import save_brand_data, load_brand_data
except Exception as e:
    st.error(f"Error loading backend modules: {e}")

def run(user_id):
    # 1. Initialize and Sync State
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
        st.caption("Determining who you are and defining your daily impact. [cite: 50, 52, 53]")
        
        # Navigation
        current_chamber_key = st.session_state.get("target_chamber", "purpus_summary")
        chamber_keys = list(chamber_map.values())
        current_idx = chamber_keys.index(current_chamber_key) if current_chamber_key in chamber_keys else 0

        selected_label = st.selectbox("Current Audit Focus:", options=list(chamber_map.keys()), index=current_idx)
        new_target = chamber_map[selected_label]

        if st.session_state.get("target_chamber") != new_target:
            st.session_state.target_chamber = new_target
            st.rerun()

        # Initial Prompt
        chamber_prompts = {
            "purpus_summary": "Foundation Phase: Why MUST this brand exist? What internal fire drives this soul? [cite: 36, 51]",
            "brand_identity": "The Foundation: If this brand were an individual, what is its identity and ethos? [cite: 53, 54]",
            "brand_experience": "Remarkable Experiences: How will your brand communicate its value while putting your audience first? [cite: 41, 43]",
            "brand_impact": "The Legacy: What urgent community problems are you solving to create ongoing impact? [cite: 52, 70]"
        }
        if not any(m.get("chamber") == new_target for m in st.session_state.messages):
            st.session_state.messages.append({"role": "assistant", "content": chamber_prompts[new_target], "chamber": new_target})

        # Chat display
        for message in [m for m in st.session_state.messages if m.get("chamber") == new_target]:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Input
        st.write("---")
        prompt = st.chat_input("Document your thoughts...")

        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt, "chamber": new_target})
            with st.chat_message("assistant"):
                with st.spinner("Unearthing deeper alignment..."):
                    
                    next_idx = current_idx + 1
                    next_key = chamber_sequence[next_idx] if next_idx < len(chamber_sequence) else "COMPLETE"
                    
                    # REFINED COMMAND LOGIC
                    methodology = f"""
                    SYSTEM CONTEXT: You are the Godzspeed Soul Rebel Facilitator. 
                    
                    MANDATORY BEHAVIOR:
                    1. DATA CAPTURE: Every insight must be captured. Wrap formal synthesis in [STRATEGY]...[/STRATEGY] tags.
                    2. PROGRESSION GATE: If the user says they are 'good' or ready to move, you MUST provide a FINAL [STRATEGY] block for the current chamber before adding the [MOVE_TO_CHAMBER:{next_key}] tag.
                    3. NO SILENT MOVES: Never move to a new chamber without confirming the previous one is documented.
                    4. APPEND: Your summaries add to the existing vision; they don't replace it.
                    
                    Current Chamber: {new_target}
                    """
                    
                    current_context = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages if m.get("chamber") == new_target])
                    full_response = get_soul_rebel_consultant(prompt, methodology + current_context)

                    # Extract strategy data
                    strategy_part = ""
                    if "[STRATEGY]" in full_response:
                        parts = full_response.split("[STRATEGY]")
                        chat_part = parts[0].strip()
                        strategy_part = parts[1].split("[/STRATEGY]")[0].strip() if "[/STRATEGY]" in parts[1] else parts[1].strip()
                    else:
                        chat_part = full_response

                    # Navigation Check
                    target_move = None
                    if "[MOVE_TO_CHAMBER:" in chat_part:
                        target_move = chat_part.split("[MOVE_TO_CHAMBER:")[1].split("]")[0]
                        chat_part = chat_part.split("[MOVE_TO_CHAMBER:")[0].strip()

                    # 1. Update Strategy/DB FIRST to ensure it appears in Documented Vision
                    if strategy_part:
                        existing = st.session_state.brand_soul.get(new_target, "")
                        combined = f"{existing}\n\n{strategy_part}".strip()
                        st.session_state.brand_soul[new_target] = combined
                        save_brand_data(user_id, combined, chamber=new_target)

                    # 2. Add chat message
                    st.session_state.messages.append({"role": "assistant", "content": chat_part, "chamber": new_target})

                    # 3. Handle move ONLY after data is saved
                    if target_move and target_move != "COMPLETE":
                        st.session_state.target_chamber = target_move
                    
                    st.rerun()

    with col2:
        st.subheader("🧬 Foundation Progress")
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
                    st.caption("Awaiting deeper unearthing... [cite: 73]")