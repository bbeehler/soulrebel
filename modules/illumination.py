import streamlit as st
import time
from utils.gemini_ai import get_soul_rebel_consultant
from utils.supabase_db import save_brand_data, load_brand_data

def run(user_id):
    st.title("✨ Phase 03: Illumination")
    st.caption("Bringing the unearthing to light through a Strategic Individual Master Document.")
    
    db_data = load_brand_data(user_id)
    brand_data = db_data if db_data else {}
    
    # 1. THE GOLD STANDARD TEMPLATE (Baked into the AI Context)
    # This structure is based on the Black Planning Project standard
    gold_standard_sections = {
        "Section 1": "Brand Identity (Big Idea, 'What it Means', Vision, Mission)", [cite: 3, 4, 5, 28, 55]
        "Section 2": "Transformation Process (Blueprint, Advocate, Inform)", [cite: 64, 73, 74, 75]
        "Section 3": "Soul Anchors (Values, Beliefs, Behaviours)", [cite: 102, 106, 158, 172]
        "Section 4": "Brand Positioning (1Soul Statement, Offering, Target Audience)", [cite: 181, 183, 197, 246]
        "Section 5": "Brand Expression (Slogan, Voice, Personality)", [cite: 311, 313, 325, 331]
        "Section 6": "Soul Ties (Brand Legacy, Key Soul Markers/KPIs)" [cite: 341, 343, 357]
    }

    # 2. THE EXPANDABLE BUILDER (Chat to deepen info)
    with st.expander("🛠️ Soul Guide Builder (Deepen the Foundation)", expanded=not st.session_state.get('final_soul_guide')):
        st.info("Use this space to add more detail or collaborate with the AI to reach the Gold Standard.")
        
        # Collaborative Chat Logic here (Similar to Discovery but focused on the Guide)
        guide_chat = st.chat_input("Add more depth to your vision here...")
        if guide_chat:
            # AI logic to specifically probe for the 6 sections above
            pass

    # 3. THE REINFORCED GENERATOR
    if st.button("🔥 Generate Gold-Standard Soul Guide", use_container_width=True):
        with st.spinner("Synthesizing your Strategic Individual..."):
            methodology = """
            TASK: Generate a Master Soul Guide following the 'Black Planning Project' benchmark.
            
            REQUIRED DEPTH:
            - Big Idea: Must be a rousing affirmation[cite: 6, 14].
            - What it Means: Deep narrative explaining the 'Why'[cite: 7, 30, 57].
            - Methodology: A 3-step 'Planning Revolution'[cite: 63, 72].
            - Soul Anchors: Convert values into specific 'We Believe' and 'We Always' behaviors[cite: 158, 172].
            - KPIs: Frame as 'Do I' questions to ensure the soul remains intact[cite: 357, 363].
            """
            
            # This uses the data from the Audit + the new Chat info
            # to build the final master document.
            guide = get_soul_rebel_consultant("Illuminate my Soul Guide.", methodology + str(brand_data))
            st.session_state.final_soul_guide = guide
            save_brand_data(user_id, guide, chamber="soul_guide")
            st.rerun()

    # 4. FINAL WORKSPACE (Text area for manual refinement)
    # ... (Same as your current workspace logic)