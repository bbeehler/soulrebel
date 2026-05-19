import streamlit as st
import time
from utils.gemini_ai import get_soul_rebel_consultant
from utils.supabase_db import get_supabase_client

def load_blueprints():
    """Fetches our strict content blueprints directly from Supabase."""
    try:
        supabase = get_supabase_client()
        response = supabase.table("brand_content_blueprints").select("*").execute()
        return response.data if response.data else []
    except Exception as e:
        st.error(f"Error loading blueprints: {e}")
        return []

def run(user_id):
    st.title("🛡️ Phase 04: The Brand Guardian")
    st.caption("Content Alignment Gatekeeper: No asset leaves the building unless it honors the Brand Soul.")
    st.write("---")

    # 1. INITIALIZE ENVIRONMENT AND SCHEMAS
    blueprints = load_blueprints()
    if not blueprints:
        st.warning("⚠️ No content blueprints found. Please verify your brand_content_blueprints table in Supabase.")
        return

    # Extract unique categories and platforms for our dropdowns
    categories = list(set([bp['category'] for bp in blueprints]))
    
    # 2. SELECTION CONFIGURATOR HUB (Sidebar or top parameters)
    st.subheader("📋 Define the Asset Parameters")
    
    col1, col2 = st.columns(2)
    with col1:
        selected_category = st.selectbox("Select Content Category:", categories)
        # Filter platforms based on the selected category to match the blueprint matrix
        available_platforms = [bp['platform'] for bp in blueprints if bp['category'] == selected_category]
        selected_platform = st.selectbox("Select Target Publishing Platform:", available_platforms)
    
    with col2:
        content_title = st.text_input("Asset Working Title:", placeholder="e.g., The Illusion of Public Inclusion")
        publish_date = st.date_input("Scheduled Publication Date:")

    # Get the specific blueprint matching the chosen parameters
    active_blueprint = next((bp for bp in blueprints if bp['category'] == selected_category and bp['platform'] == selected_platform), None)

    if active_blueprint:
        with st.expander("🔍 View Active Blueprint Guardrails", expanded=False):
            st.markdown(f"**Medium Format:** {active_blueprint['medium_type']}")
            st.markdown(f"**Target Depth/Length:** {active_blueprint['target_length']}")
            st.markdown(f"**Strict Tonal Rules:** *{active_blueprint['tonal_guardrails']}*")
            st.markdown(f"**Strict Structural Mandates:** {active_blueprint['structural_rules']}")

    st.write("---")

    # 3. INITIALIZATION OF WORKSPACE PERSISTENCE
    if "guardian_suggestion" not in st.session_state:
        st.session_state.guardian_suggestion = ""
    if "workspace_text" not in st.session_state:
        st.session_state.workspace_text = ""
    if "guardian_rev" not in st.session_state:
        st.session_state.guardian_rev = 0

    # 4. IDEATION & GENERATION LAYER
    st.subheader("💡 Content Generation & Optimization")
    
    if st.button("✨ Generate Strategic Suggestion from Playbook", use_container_width=True):
        with st.spinner("Analyzing your Master Soul Guide and crafting blueprint-aligned copy..."):
            try:
                supabase = get_supabase_client()
                # Fetch the master compiled soul guide from phase 3 to use as context
                strategy_res = supabase.table("brand_strategy").select("soul_guide").eq("user_id", user_id).single().execute()
                soul_guide_context = strategy_res.data.get("soul_guide", "") if strategy_res.data else ""
                
                if not soul_guide_context:
                    st.error("🚨 Master Soul Guide not found. Please complete Phase 03: Illumination before planning content.")
                    return

                # Instruct the AI to build high-fidelity copy using the structural matrix rules
                prompt = f"""
                ROLE: Godzspeed Soul Rebel Brand Guardian.
                TASK: Generate a piece of ready-to-publish raw copy for the asset title: '{content_title}'.
                
                STRICT COMPLIANCE MATRIX PARAMETERS:
                - Category: {selected_category}
                - Platform: {selected_platform}
                - Format Target: {active_blueprint['medium_type']}
                - Length Target: {active_blueprint['target_length']}
                - Tone Rules: {active_blueprint['tonal_guardrails']}
                - Structural Rules: {active_blueprint['structural_rules']}
                
                MASTER TONAL PLAYBOOK (Use this as your source of truth for vocabulary, rhythm, and purpose):
                {soul_guide_context}
                
                OUTPUT: Provide only the fully-written copy. Do not add intro greetings, conversational prefaces, or placeholders. Speak with poetic, commanding, elite 'hella smart' authority.
                """
                
                suggestion = get_soul_rebel_consultant(f"Generate content for {content_title}", prompt)
                st.session_state.guardian_suggestion = suggestion
                st.success("High-fidelity strategic suggestion generated below!")
            except Exception as e:
                st.error(f"Handshake failure loading strategy context: {e}")

    # Display the AI Suggestion box if content has been generated
    if st.session_state.guardian_suggestion:
        st.info("### 🤖 Brand Guardian Raw Suggestion")
        st.write(st.session_state.guardian_suggestion)
        
        # Interactive Control Buttons for the Suggestion
        s_col1, s_col2 = st.columns(2)
        with s_col1:
            if st.button("✅ Accept & Move to Active Workspace", use_container_width=True, type="primary"):
                st.session_state.workspace_text = st.session_state.guardian_suggestion
                st.session_state.guardian_rev += 1
                st.rerun()
        with s_col2:
            if st.button("❌ Reject Suggestion", use_container_width=True):
                st.session_state.guardian_suggestion = ""
                st.rerun()

    # 5. ACTIVE LIVE WORKSPACE (Where the user refines and types)
    st.write("---")
    st.subheader("📝 Active Asset Workspace")
    
    # Versioned key prevents widget shadowing when accepting a suggestion or updating via chat
    workspace_key = f"guardian_text_area_v{st.session_state.guardian_rev}"
    
    edited_body = st.text_area(
        "Refine, write, or manually format your asset here:",
        value=st.session_state.workspace_text,
        height=400,
        key=workspace_key,
        help="This is the text that must pass the final compliance check before moving to the publishing calendar."
    )
    # Sync typing changes into memory state
    st.session_state.workspace_text = edited_body

    # 6. COLLABORATIVE AI REFINEMENT HUB (Braid details or feedback into the text box)
    if st.session_state.workspace_text:
        st.write("---")
        user_feedback = st.chat_input("Ask the Guardian to rewrite, expand, or fix tone issues for this asset...")
        
        if user_feedback:
            with st.spinner("Recalibrating asset against the corporate blueprint..."):
                refine_prompt = f"""
                ROLE: Godzspeed Soul Rebel Brand Guardian.
                TASK: Revise the EXISTING TEXT based on the USER FEEDBACK.
                
                CRITICAL LIMITS:
                - Honor the active platform parameters: Category: {selected_category}, Platform: {selected_platform}.
                - Strictly maintain the tone guidelines: {active_blueprint['tonal_guardrails']}.
                - Do not lose structural integrity. Return ONLY the complete revised text block.
                
                EXISTING TEXT:
                {edited_body}
                """
                
                revised_text = get_soul_rebel_consultant(user_feedback, refine_prompt)
                st.session_state.workspace_text = revised_text
                st.session_state.guardian_rev += 1
                st.rerun()