import streamlit as st
import time

try:
    from utils.gemini_ai import get_soul_rebel_consultant
    from utils.supabase_db import save_brand_data, load_brand_data
except Exception as e:
    st.error(f"Error loading backend modules: {e}")

def run(user_id):
    # 1. Initialize State
    if "brand_soul" not in st.session_state:
        st.session_state.brand_soul = load_brand_data(user_id) or {}
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "widget_seeds" not in st.session_state:
        st.session_state.widget_seeds = {k: 0 for k in ["purpus_summary", "brand_identity", "brand_experience", "brand_impact"]}

    chamber_map = {
        "✨ Soul (PurpUS)": "purpus_summary",
        "🎭 Mind (Identity)": "brand_identity",
        "🌟 Body (Experience)": "brand_experience",
        "🌍 Body (Impact)": "brand_impact"
    }
    chamber_sequence = ["purpus_summary", "brand_identity", "brand_experience", "brand_impact"]
    
    # --- NAVIGATION ---
    current_chamber_key = st.session_state.get("target_chamber", "purpus_summary")
    chamber_keys = list(chamber_map.values())
    current_idx = chamber_keys.index(current_chamber_key)
    
    col1, col2 = st.columns([3, 2])

    with col1:
        st.title("🔥 The Soul Audit")
        st.caption(f"Unearthing Phase: {list(chamber_map.keys())[current_idx]}")
        
        # 1. FACILITATOR CHAT
        chamber_prompts = {
            "purpus_summary": "Foundation Phase: Why MUST this brand exist? What internal fire drives this soul?",
            "brand_identity": "The Foundation: If this brand were an individual, what is its identity and ethos?",
            "brand_experience": "Remarkable Experiences: How will your brand communicate its value while putting your audience first?",
            "brand_impact": "The Legacy: What urgent community problems are you solving to create ongoing impact?"
        }
        
        # Ensure the opening prompt exists for the current chamber
        if not any(m.get("chamber") == current_chamber_key for m in st.session_state.messages):
            st.session_state.messages.append({"role": "assistant", "content": chamber_prompts[current_chamber_key], "chamber": current_chamber_key})

        # Display persistent chat history for this chamber
        for message in [m for m in st.session_state.messages if m.get("chamber") == current_chamber_key]:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        st.write("---")
        audio_input = st.audio_input("🎤 Speak your vision", key=f"audio_{current_chamber_key}")
        prompt = st.chat_input("Unearth your thoughts...")

        user_input = None
        if audio_input:
            audio_id = hash(f"{audio_input.name}_{audio_input.size}")
            if st.session_state.get("last_audio_id") != audio_id:
                user_input = "🎤 *Voice Vision Submitted*"
                st.session_state.last_audio_id = audio_id
        elif prompt:
            user_input = prompt

        if user_input:
            st.session_state.messages.append({"role": "user", "content": user_input, "chamber": current_chamber_key})
            with st.chat_message("assistant"):
                with st.spinner("Processing unearthing..."):
                    methodology = f"""
                    ROLE: Godzspeed Facilitator. 
                    TASK: Challenge the user. Probe deeper. Do not move on. 
                    STRATEGY TAGS: Every time the user provides substance, summarize the cumulative findings inside [STRATEGY]...[/STRATEGY] tags.
                    """
                    current_context = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages if m.get("chamber") == current_chamber_key])
                    full_response = get_soul_rebel_consultant(user_input, methodology + current_context)

                    # Extract Strategy Draft
                    if "[STRATEGY]" in full_response:
                        parts = full_response.split("[STRATEGY]")
                        chat_part = parts[0].strip()
                        strategy_draft = parts[1].split("[/STRATEGY]")[0].strip() if "[/STRATEGY]" in parts[1] else parts[1].strip()
                        st.session_state[f"draft_{current_chamber_key}"] = strategy_draft
                    else:
                        chat_part = full_response

                    st.session_state.messages.append({"role": "assistant", "content": chat_part, "chamber": current_chamber_key})
                    st.rerun()

    with col2:
        st.subheader("📋 Documented Vision")
        st.info("Review the unearthing. Edit to refine, or Commit to advance.")

        # RESTORED: Edit Mode Toggle
        edit_mode = st.toggle("🛠️ Enable Manual Edit Mode")

        draft_content = st.session_state.get(f"draft_{current_chamber_key}", "")
        saved_content = st.session_state.brand_soul.get(current_chamber_key, "")
        display_text = draft_content if draft_content else saved_content

        with st.expander("🔍 Proposed Strategic Individual", expanded=True):
            if edit_mode:
                # Restoration of Manual Editing and Saving
                dk = f"widget_{current_chamber_key}_{st.session_state.widget_seeds[current_chamber_key]}"
                final_text = st.text_area("Refine Summary:", value=display_text, height=350, key=dk)
                
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("💾 Save Changes", use_container_width=True):
                        st.session_state.brand_soul[current_chamber_key] = final_text
                        save_brand_data(user_id, final_text, chamber=current_chamber_key)
                        st.success("Draft Saved.")
                        time.sleep(0.5)
                        st.rerun()
                with c2:
                    if st.button("🗑️ Clear Phase", use_container_width=True):
                        st.session_state.brand_soul[current_chamber_key] = ""
                        st.session_state[f"draft_{current_chamber_key}"] = ""
                        save_brand_data(user_id, "", chamber=current_chamber_key)
                        # Reset chat history for this chamber only
                        st.session_state.messages = [m for m in st.session_state.messages if m.get("chamber") != current_chamber_key]
                        st.session_state.widget_seeds[current_chamber_key] += 1
                        st.rerun()
            else:
                st.markdown(display_text if display_text else "*Awaiting unearthing...*")
                final_text = display_text

        # THE GATE
        if final_text and not edit_mode:
            if st.button("🔥 Commit & Advance Phase", use_container_width=True):
                st.session_state.brand_soul[current_chamber_key] = final_text
                save_brand_data(user_id, final_text, chamber=current_chamber_key)
                
                if current_idx < 3:
                    next_key = chamber_sequence[current_idx + 1]
                    st.session_state.target_chamber = next_key
                    st.success(f"Phase {current_idx + 1} Committed.")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.balloons()
                    st.success("Soul Audit Complete!")

        st.write("---")
        st.subheader("🧬 Foundation History")
        for label, key in chamber_map.items():
            if key != current_chamber_key:
                with st.expander(label):
                    st.markdown(st.session_state.brand_soul.get(key, "*Awaiting unearthing...*"))