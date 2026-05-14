import streamlit as st
import time

try:
    from utils.gemini_ai import get_soul_rebel_consultant
    from utils.supabase_db import save_brand_data, load_brand_data
except Exception as e:
    st.error(f"Error loading backend modules: {e}")

def run(user_id):
    # 1. Initialize State & Soul Alignment
    if "brand_soul" not in st.session_state:
        saved_data = load_brand_data(user_id)
        st.session_state.brand_soul = saved_data if saved_data else {}
    
    if "widget_seeds" not in st.session_state:
        st.session_state.widget_seeds = {k: 0 for k in ["purpus_summary", "brand_identity", "brand_experience", "brand_impact"]}
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Map Chambers to Godzspeed Phase 02: Foundation
    chamber_map = {
        "✨ Phase 02: PurpUS (Soul)": "purpus_summary",
        "🎭 Phase 02: Identity (Mind)": "brand_identity",
        "🌟 Phase 02: Experience (Body)": "brand_experience",
        "🌍 Phase 02: Impact (Body)": "brand_impact"
    }
    
    chamber_sequence = ["purpus_summary", "brand_identity", "brand_experience", "brand_impact"]
    
    # Methodology-Driven Prompts
    chamber_prompts = {
        "purpus_summary": "Welcome to the Vision Retreat. We are unearthing the foundation for your growth. Forget what you sell—Why MUST this brand exist? What is the 'internal fire' and the shared PurpUS that will rally your community?",
        "brand_identity": "Let's define the Individual. We are designing an empathetic, inspiring, and influential organizational culture. If this brand were a person, what are its core values, beliefs, and aspirations?",
        "brand_experience": "Remarkable Experiences. Beyond visuals, how will experiential activations and brand ethos convey your soul? Describe the ritual that turns clients into energized ambassadors.",
        "brand_impact": "The Legacy. We are positioning you for meaningful impact. How does this Individual solve urgent community problems and create social or environmental change in the industry?"
    }

    col1, col2 = st.columns([3, 2])

    with col1:
        st.title("🔥 The Soul Audit")
        st.caption("Godzspeed Phase 02: Foundation — Reaching the deepest level of understanding.")
        
        # --- DYNAMIC SELECTOR ---
        current_chamber_key = st.session_state.get("target_chamber", "purpus_summary")
        chamber_labels = list(chamber_map.keys())
        chamber_keys = list(chamber_map.values())
        current_idx = chamber_keys.index(current_chamber_key) if current_chamber_key in chamber_keys else 0

        selected_label = st.selectbox("Current Audit Focus:", options=chamber_labels, index=current_idx)
        new_target = chamber_map[selected_label]

        if st.session_state.get("target_chamber") != new_target:
            st.session_state.target_chamber = new_target
            st.rerun()

        # Ensure opening prompt exists
        chamber_has_messages = any(m.get("chamber") == new_target for m in st.session_state.messages)
        if not chamber_has_messages:
            st.session_state.messages.append({"role": "assistant", "content": chamber_prompts[new_target], "chamber": new_target})

        # --- CHAT DISPLAY ---
        active_messages = [m for m in st.session_state.messages if m.get("chamber") == new_target]
        for i, message in enumerate(active_messages):
            if i == 0 and len(active_messages) > 3: continue
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Completion Logic
        brand_data = st.session_state.get('brand_soul', {})
        if all(brand_data.get(k) for k in chamber_sequence):
            st.success("🎉 **Soul Audit Complete.** The Foundation is documented.")
            st.info("You are ready for Phase 03: Illumination. Select 'The Soul Guide' to synthesize your vision.")
            if st.button("Celebrate Alignment"):
                st.balloons()

        # --- INPUT HANDLING ---
        st.write("---")
        audio_input = st.audio_input("🎤 Speak your vision", key="soul_audio_recorder")
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
            st.session_state.messages.append({"role": "user", "content": user_input_content, "chamber": new_target})
            
            with st.chat_message("assistant"):
                with st.spinner("Analyzing Soul Alignment..."):
                    next_idx = chamber_sequence.index(new_target) + 1
                    next_chamber_key = chamber_sequence[next_idx] if next_idx < len(chamber_sequence) else "COMPLETE"
                    
                    # INJECTING GODZSPEED & JB MEDIA PHILOSOPHY
                    system_methodology = """
                    SYSTEM CONTEXT: You are a Godzspeed Soul Rebel Facilitator. 
                    You are currently in Phase 02: Foundation (The Soul Audit).
                    
                    GOAL: Unearth, plan, and document the business vision. 
                    1. Focus on deep 'Soul Alignment'. 
                    2. Seek 'Remarkable Experiences' and 'Authentic Storytelling'.
                    3. Prioritize 'Impact Positioning'—how the brand solves community problems.
                    4. Aim for 'Brand Affinity' and 'Love Affairs' between community and brand.
                    
                    Be tactful, experienced, and encouraging.
                    """
                    
                    instruction = (
                        f"\n\nReflection: Provide a strategic response. Place formal documentation inside [STRATEGY] tags. "
                        f"If the vision for this section is solidified, add [MOVE_TO_CHAMBER:{next_chamber_key}] at the end."
                    )
                    
                    current_context = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages if m.get("chamber") == new_target])
                    full_response = get_soul_rebel_consultant(user_input_content, system_methodology + current_context + instruction)

                    if "[STRATEGY]" in full_response:
                        parts = full_response.split("[STRATEGY]")
                        chat_part = parts[0].strip()
                        strategy_part = parts[1].split("[/STRATEGY]")[0].strip() if "[/STRATEGY]" in parts[1] else parts[1].strip()
                    else:
                        chat_part, strategy_part = full_response, full_response

                    if "[MOVE_TO_CHAMBER:" in chat_part:
                        move_tag = chat_part.split("[MOVE_TO_CHAMBER:")[1].split("]")[0]
                        chat_part = chat_part.split("[MOVE_TO_CHAMBER:")[0].strip()
                        if move_tag != "COMPLETE":
                            st.session_state.target_chamber = move_tag
                            st.session_state.messages.append({"role": "assistant", "content": f"🎯 **Foundation Solidified.**\n\n{chamber_prompts[move_tag]}", "chamber": move_tag})

                    clean_chat = chat_part.replace("[STRATEGY]", "").replace("[/STRATEGY]", "").strip()
                    st.session_state.messages.append({"role": "assistant", "content": clean_chat, "chamber": new_target})
                    st.session_state.brand_soul[new_target] = strategy_part
                    save_brand_data(user_id, strategy_part, chamber=new_target)

            st.rerun()

    with col2:
        st.subheader("🧬 Discovery Progress")
        filled = sum(1 for k in chamber_sequence if brand_data.get(k))
        st.progress(filled/4)

        st.write("---")
        st.subheader("📋 Documented Vision")
        edit_mode = st.toggle("🛠️ Edit Strategy Foundation")

        for label, key in chamber_map.items():
            is_expanded = (st.session_state.get("target_chamber") == key)
            with st.expander(label, expanded=is_expanded):
                content = brand_data.get(key, "")
                if edit_mode:
                    dk = f"widget_{key}_{st.session_state.widget_seeds[key]}"
                    new_val = st.text_area(f"Refine {label}:", value=content, height=200, key=dk)
                    if st.button(f"💾 Update {label}", key=f"s_{key}"):
                        st.session_state.brand_soul[key] = new_val
                        save_brand_data(user_id, new_val, chamber=key)
                        st.success("Foundation Updated.")
                        time.sleep(0.5)
                        st.rerun()
                else:
                    if content:
                        st.markdown(content)
                    else:
                        st.caption("Awaiting Soul Audit...")