import streamlit as st
import datetime
import time
from utils.gemini_ai import get_soul_rebel_consultant
from utils.supabase_db import supabase

def load_blueprints():
    """Fetches strict content blueprints matrix from Supabase."""
    try:
        response = supabase.table("brand_content_blueprints").select("*").execute()
        return response.data if response.data else []
    except Exception as e:
        st.error(f"Error loading blueprints: {e}")
        return []

def load_content_calendar(user_id):
    """Fetches all planned, drafted, and committed assets for the user."""
    try:
        response = supabase.table("brand_content_items").select("*").eq("user_id", user_id).order("publish_date").execute()
        return response.data if response.data else []
    except Exception as e:
        st.error(f"Error pulling calendar pipeline: {e}")
        return []

def run(user_id):
    st.title("🛡️ Phase 04: The Brand Guardian")
    st.caption("Content Alignment Gatekeeper & Omni-Channel Scheduling Matrix.")
    st.write("---")

    # INITIALIZE ENVIRONMENT DATA
    blueprints = load_blueprints()
    if not blueprints:
        st.warning("⚠️ No content blueprints configured. Please run your reference database migrations.")
        return

    categories = list(set([bp['category'] for bp in blueprints]))

    # SAFE STATE FOR CONFIGURATION OVERRIDES
    if "override_cat" not in st.session_state:
        st.session_state.override_cat = categories[0]
        
    init_plats = [bp['platform'] for bp in blueprints if bp['category'] == st.session_state.override_cat]
    if "override_plat" not in st.session_state:
        st.session_state.override_plat = init_plats[0] if init_plats else ""
        
    if "override_title" not in st.session_state:
        st.session_state.override_title = ""
    if "override_date" not in st.session_state:
        st.session_state.override_date = datetime.date.today()

    if "guardian_suggestion" not in st.session_state:
        st.session_state.guardian_suggestion = ""
    if "workspace_text" not in st.session_state:
        st.session_state.workspace_text = ""
    if "compliance_report" not in st.session_state:
        st.session_state.compliance_report = None
    if "last_loaded_key" not in st.session_state:
        st.session_state.last_loaded_key = ""
    if "guardian_rev" not in st.session_state:
        st.session_state.guardian_rev = 0

    # --- SPLIT LAYOUT: MAIN STEPS WORKSPACE VS RIGHT SIDEBAR SCHEDULING BAR ---
    col_main, col_sidebar = st.columns([5, 2], gap="large")

    with col_main:
        # =====================================================================
        # STEP 1: PARAMETER CONFIGURATION
        # =====================================================================
        st.markdown("### 🏷️ Step 1: Set Asset Campaign Parameters")
        
        col1, col2 = st.columns(2)
        with col1:
            try:
                cat_idx = categories.index(st.session_state.override_cat)
            except ValueError:
                cat_idx = 0
                
            selected_category = st.selectbox(
                "Select Content Category Pillar:", 
                categories, 
                index=cat_idx,
                help="Choose the foundational marketing pillar this piece of content addresses."
            )
            st.session_state.override_cat = selected_category
            
            available_platforms = [bp['platform'] for bp in blueprints if bp['category'] == selected_category]
            
            try:
                plat_idx = available_platforms.index(st.session_state.override_plat)
            except ValueError:
                plat_idx = 0
                
            selected_platform = st.selectbox(
                "Target Publishing Platform / Channel:", 
                available_platforms, 
                index=plat_idx,
                help="Select the digital distribution channel where this copy will be published."
            )
            st.session_state.override_plat = selected_platform
        
        with col2:
            content_title = st.text_input(
                "Asset Working Title:", 
                value=st.session_state.override_title, 
                placeholder="e.g., The Illusion of Public Inclusion",
                help="Type a unique, recognizable title for this campaign item."
            )
            st.session_state.override_title = content_title
            
            publish_date = st.date_input(
                "Scheduled Publication Date:", 
                value=st.session_state.override_date,
                help="Choose the target deployment date for your publishing pipeline."
            )
            st.session_state.override_date = publish_date

        active_blueprint = next((bp for bp in blueprints if bp['category'] == selected_category and bp['platform'] == selected_platform), None)

        if active_blueprint:
            with st.expander("🔍 View Active Channel Blueprint Guardrails", expanded=False):
                st.markdown(f"**Medium Format:** {active_blueprint['medium_type']}")
                st.markdown(f"**Target Depth/Length:** {active_blueprint['target_length']}")
                st.markdown(f"**Strict Tonal Rules:** *{active_blueprint['tonal_guardrails']}*")
                st.markdown(f"**Strict Structural Mandates:** {active_blueprint['structural_rules']}")

        # DATA ENGINE SYNCHRONIZATION HANDSHAKE
        current_asset_key = f"{selected_platform}_{content_title}_{publish_date}"
        if st.session_state.last_loaded_key != current_asset_key and content_title:
            try:
                existing_res = supabase.table("brand_content_items")\
                    .select("*")\
                    .eq("user_id", user_id)\
                    .eq("title", content_title)\
                    .eq("platform", selected_platform)\
                    .eq("publish_date", str(publish_date))\
                    .execute()
                    
                if existing_res.data:
                    asset_record = existing_res.data[0]
                    st.session_state.workspace_text = asset_record.get("current_body", "")
                    st.session_state.guardian_suggestion = asset_record.get("suggested_body", "")
                    st.session_state.compliance_report = asset_record.get("guardian_notes", "")
                else:
                    st.session_state.workspace_text = ""
                    st.session_state.guardian_suggestion = ""
                    st.session_state.compliance_report = None
                    
                st.session_state.last_loaded_key = current_asset_key
            except Exception:
                pass

        st.write("---")

        # =====================================================================
        # STEP 2: BLUEPRINT COMPLIANT GENERATION
        # =====================================================================
        st.markdown("### 💡 Step 2: Playbook Synthesis Suggestion")
        
        if st.button(
            "✨ Generate Strategic Suggestion from Playbook", 
            use_container_width=True,
            help="Click to prompt Gemini to draft a high-fidelity copy outline rooted completely in your Phase 03 Soul Guide."
        ):
            if not content_title:
                st.error("Please fill in an Asset Working Title to provide contextual fuel for generation.")
            else:
                with st.spinner("Analyzing your Master Soul Guide and crafting blueprint-aligned copy..."):
                    try:
                        strategy_res = supabase.table("brand_strategy").select("soul_guide").eq("user_id", user_id).single().execute()
                        soul_guide_context = strategy_res.data.get("soul_guide", "") if strategy_res.data else ""
                        
                        if not soul_guide_context:
                            st.error("🚨 Master Soul Guide context not found. Please complete Phase 03: Illumination first.")
                            return

                        prompt = f"""
                        ROLE: Godzspeed Soul Rebel Brand Guardian.
                        TASK: Generate ready-to-publish raw copy for the asset title: '{content_title}'.
                        
                        STRICT COMPLIANCE MATRIX PARAMETERS:
                        - Category: {selected_category} | Platform: {selected_platform}
                        - Format Target: {active_blueprint['medium_type']} | Length Target: {active_blueprint['target_length']}
                        - Tone Rules: {active_blueprint['tonal_guardrails']}
                        - Structural Rules: {active_blueprint['structural_rules']}
                        
                        MASTER TONAL PLAYBOOK CONTEXT:
                        {soul_guide_context}
                        
                        OUTPUT: Provide only the fully-written copy block matching these parameters. Speak with poetic, commanding, elite 'hella smart' authority.
                        """
                        suggestion = get_soul_rebel_consultant(f"Generate content for {content_title}", prompt)
                        st.session_state.guardian_suggestion = suggestion
                        st.success("High-fidelity strategic suggestion generated below!")
                    except Exception as e:
                        st.error(f"Handshake failure loading strategy context: {e}")

        if st.session_state.guardian_suggestion:
            st.info("### 🤖 Brand Guardian Raw Suggestion")
            st.write(st.session_state.guardian_suggestion)
            s_col1, s_col2 = st.columns(2)
            with s_col1:
                if st.button("✅ Accept & Move to Active Workspace", use_container_width=True, type="primary"):
                    st.session_state.workspace_text = st.session_state.guardian_suggestion
                    st.session_state.guardian_rev += 1  
                    st.success("Copy seamlessly transferred to active workspace!")
                    time.sleep(0.5)
                    st.rerun()
            with s_col2:
                if st.button("❌ Reject Suggestion", use_container_width=True):
                    st.session_state.guardian_suggestion = ""
                    st.rerun()

        st.write("---")

        # =====================================================================
        # STEP 3: SPECIFIC ACTIVE LIVE WORKSPACE
        # =====================================================================
        st.markdown(f"### 📝 Step 3: Active Composition Workspace")
        st.caption(f"Currently managing workspace data for: **{content_title if content_title else 'Untitled Asset'}** targeted for rollout on **{publish_date}**.")
        
        workspace_key = f"main_editor_rev_{st.session_state.guardian_rev}"
        
        edited_body = st.text_area(
            "Refine, write, or manually format your asset here:",
            value=st.session_state.workspace_text,
            height=350,
            key=workspace_key,
            help="The active drawing board for your content asset. Copy can be modified manually or via conversational chat prompts down below."
        )
        st.session_state.workspace_text = edited_body

        if st.session_state.workspace_text:
            user_feedback = st.chat_input("Ask the Guardian to rewrite, expand, or adjust tone parameters for this workspace...")
            if user_feedback:
                with st.spinner("Recalibrating asset against the corporate blueprint..."):
                    refine_prompt = f"""
                    ROLE: Godz