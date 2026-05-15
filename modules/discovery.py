import streamlit as st
import time

try:
    from utils.gemini_ai import get_soul_rebel_consultant
    from utils.supabase_db import save_brand_data, load_brand_data
except Exception as e:
    st.error(f"Error loading backend modules: {e}")

def run(user_id):
    # 1. INITIALIZE & SYNC
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
    
    # 2. CHAMBER NAVIGATION
    current_chamber_key = st.session_state.get("target_chamber", "purpus_summary")
    chamber_keys = list(chamber_map.values())
    current_idx = chamber_keys.index(current_chamber_key)
    current_label = list(chamber_map.keys())[current_idx]
    
    col1, col2 = st.columns([3, 2])

    with col1:
        st.title("🔥 The Soul Audit")
        st.caption(f"Facilitated Unearthing: {current_label}")
        
        chamber_prompts = {
            "purpus_summary": "Foundation Phase: Why MUST this brand exist? What internal fire drives this soul?",
            "brand_identity": "The Foundation: If this brand were an individual, what is its identity and ethos?",
            "brand_experience": "Remarkable Experiences: How will your brand communicate its value while putting your audience first?",
            "brand_impact": "The Legacy: What urgent community problems are you solving to create ongoing impact?"
        }
        
        if not any(m.get("chamber") == current_chamber_key for m in st.session_state.messages):
            st.session_state.messages.append({"role": "assistant", "content": chamber_prompts[current_chamber_key], "chamber": current_chamber_key})

        for message in [m for m in st.session_state.messages if m.get("chamber") == current_chamber_key]:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        st.write("---")
        audio_input = st.audio_input("🎤 Speak your vision", key=f"audio_input_{current_chamber_key}")
        prompt = st.chat_input("Document your thoughts...")

        user_input_content = None
        if audio_input:
            audio_id = hash(f"{audio_input.name}_{audio_input.size}")
            if st.session_state.get("last_audio_id") != audio_id:
                user_input_content = "🎤 *Voice Vision Submitted*"
                st.session_state.last_audio_id = audio_id
        elif prompt:
            user_input_content = prompt

        if user_input_content:
            st.session_state.messages.append({"role": "user", "content": user_input_content, "chamber": current_chamber_key})
            with st.chat_message("assistant"):
                with st.spinner("Updating strategic vision..."):
                    methodology = f"""
                    ROLE: Godzspeed Facilitator. 
                    CURRENT PHASE: {current_label} ({current_chamber_key})
                    TASK: Challenge the user's input. Probe for deeper layers. 
                    MANDATORY: Synthesize the current conversation into a cumulative summary for this phase.
                    Wrap the updated synthesis in [STRATEGY]...[/STRATEGY] tags.
                    """
                    current_context = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages if m.get("chamber") == current_chamber_key])
                    full_response = get_soul_rebel_consultant(user_input_content, methodology + current_context)

                    strategy_draft = ""
                    if "[STRATEGY]" in full_response:
                        parts = full_response.split("[STRATEGY]")
                        chat_part = parts[0].strip()
                        strategy_draft = parts[1].split("[/STRATEGY]")[0].strip() if "[/STRATEGY]" in parts[1] else parts[1].strip()
                    else:
                        chat_part = full_response
                        if len(full_response) > 200:
                            strategy_draft = full_response

                    if strategy_draft:
                        st.session_state[f"active_draft_{current_chamber_key}"] = strategy_draft

                    st.session_state.messages.append({"role": "assistant", "content": chat_part, "chamber": current_chamber_key})
                    st.rerun()

    with col2:
        st.subheader("📋 Documented Vision")
        edit_mode = st.toggle("🛠️ Manual Edit Mode", key=f"edit_toggle_{current_chamber_key}")

        draft_content = st.session_state.get(f"active_draft_{current_chamber_key}", "")
        saved_content = st.session_state.brand_soul.get(current_chamber_key, "")
        display_text = draft_content if draft_content else saved_content

        with st.expander(f"🔍 Proposed: {current_label}", expanded=True):
            if edit_mode:
                widget_key = f"refine_{current_chamber_key}_{st.session_state.widget_seeds[current_chamber_key]}"
                final_text = st.text_area("Refine Summary:", value=display_text, height=350, key=widget_key)
                
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("💾 Save Changes", key=f"save_btn_{current_chamber_key}", use_container_width=True):
                        st.session_state.brand_soul[current_chamber_key] = final_text
                        save_brand_data(user_id, final_text, chamber=current_chamber_key)
                        st.success("Vision Updated.")
                        st.rerun()
                with c2:
                    if st.button("🗑️ Clear Phase", key=f"reset_btn_{current_chamber_key}", use_container_width=True):
                        st.session_state.brand_soul[current_chamber_key] = ""
                        st.session_state[f"active_draft_{current_chamber_key}"] = ""
                        save_brand_data(user_id, "", chamber=current_chamber_key)
                        st.session_state.messages = [m for m in st.session_state.messages if m.get("chamber") != current_chamber_key]
                        st.session_state.widget_seeds[current_chamber_key] += 1
                        st.rerun()
            else:
                if display_text:
                    st.markdown(display_text)
                else:
                    st.caption("Awaiting Facilitator synthesis...")
                final_text = display_text

        # 3. THE COMMIT & TRANSITION GATE
        if final_text and not edit_mode:
            is_last_phase = (current_idx == 3)
            button_label = "🔥 Finalize Audit & Illuminate Soul Guide" if is_last_phase else "🔥 Commit & Advance Phase"
            
            if st.button(button_label, use_container_width=True, key=f"commit_btn_{current_chamber_key}"):
                # Always Save First
                st.session_state.brand_soul[current_chamber_key] = final_text
                save_brand_data(user_id, final_text, chamber=current_chamber_key)
                
                if not is_last_phase:
                    # Move to next sub-phase
                    next_key = chamber_sequence[current_idx + 1]
                    st.session_state.target_chamber = next_key
                    if f"active_draft_{next_key}" in st.session_state:
                        del st.session_state[f"active_draft_{next_key}"]
                    st.success(f"Phase committed.")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    # FINAL COMPLETION: FORCE REDIRECT TO ILLUMINATION
                    st.balloons()
                    st.session_state.audit_complete = True
                    
                    # MATCHING THE NAVIGATION KEYS IN YOUR APP
                    st.session_state.target_page = "✨ Phase 03: Illumination"
                    st.session_state.page = "illumination" 
                    
                    st.success("Audit Complete! Igniting the Soul Guide...")
                    time.sleep(1.5)
                    st.rerun()

        st.write("---")
        st.subheader("🧬 Foundation History")
        for label, key in chamber_map.items():
            if key != current_chamber_key:
                with st.expander(label):
                    hist = st.session_state.brand_soul.get(key, "")
                    st.markdown(hist if hist else "*Awaiting unearthing...*")