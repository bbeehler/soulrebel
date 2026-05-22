import streamlit as st
import datetime
import time
from utils.gemini_ai import get_soul_rebel_consultant
from utils.supabase_db import supabase

# =====================================================================
# HARD PLATFORM API SPECIFICATIONS MATRIX
# =====================================================================
PLATFORM_LIMITS = {
    "Facebook": {
        "char_max": 5000,
        "ideal_image": "1080 x 1080 px (Square) or 1200 x 628 px (Landscape)",
        "aspect_ratio": "1:1 or 1.91:1",
        "safe_zone": "Front-load primary hooks within the first 125 characters before the 'See More' truncation cutoff."
    },
    "Instagram": {
        "char_max": 2200,
        "ideal_image": "1080 x 1350 px (Portrait 4:5 Default) or 1080 x 1920 px (Reels 9:16)",
        "aspect_ratio": "4:5 or 9:16",
        "safe_zone": "For Reels/Stories, leave top 15% and bottom 20% clear of text overlays to protect against UI buttons."
    },
    "LinkedIn": {
        "char_max": 3000,
        "ideal_image": "1200 x 1200 px (Square) or 1080 x 1350 px (Mobile Carousel Document View)",
        "aspect_ratio": "1:1 or 4:5",
        "safe_zone": "Engage readers completely within the first 140-210 characters before truncation sets in."
    },
    "TikTok": {
        "char_max": 2200,
        "ideal_image": "1080 x 1920 px (Vertical Video/Carousel 9:16 Format)",
        "aspect_ratio": "9:16 Vert",
        "safe_zone": "Keep interactive text clear of the top 120px header and bottom 250px engagement bar rails."
    },
    "Website Blog": {"char_max": 99999, "ideal_image": "1200 x 630 px (OG Graph Header)", "aspect_ratio": "1.91:1", "safe_zone": "Standard SEO metadata guidelines apply."},
    "Substack Blog": {"char_max": 99999, "ideal_image": "1200 x 600 px (Feature Banner Banner)", "aspect_ratio": "2:1", "safe_zone": "Optimized for continuous, clean newsletter reading streams."},
    "Internal Intranet": {"char_max": 20000, "ideal_image": "Full Screen Responsive Banner", "aspect_ratio": "Variable Layout", "safe_zone": "Internal corporate network bounds apply."}
}

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
    st.title("The Brand Guardian")
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
                help="Choose the foundational strategic pillar this piece of content addresses."
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
        plat_specs = PLATFORM_LIMITS.get(selected_platform, {"char_max": 5000, "ideal_image": "1080x1080", "aspect_ratio": "1:1", "safe_zone": "None"})

        # Native Integration of API constraints right inside your expanded blueprint display
        if active_blueprint:
            with st.expander("🔍 View Active Channel Blueprint & Platform Constraints", expanded=True):
                c_spec1, c_spec2 = st.columns(2)
                with c_spec1:
                    st.markdown("**📋 Strategy Directives**")
                    st.markdown(f"- **Format:** {active_blueprint['medium_type']}")
                    st.markdown(f"- **Target Depth:** {active_blueprint['target_length']}")
                    st.markdown(f"- **Structural Rules:** {active_blueprint['structural_rules']}")
                with c_spec2:
                    st.markdown("**📱 Hard Platform API Specifications**")
                    st.markdown(f"- **Max Character Limit:** `{plat_specs['char_max']:,}` characters")
                    st.markdown(f"- **Ideal Resolution:** `{plat_specs['ideal_image']}`")
                    st.markdown(f"- **Required Aspect Ratio:** `{plat_specs['aspect_ratio']}`")
                st.write(" ")
                st.markdown(f"⚠️ **Safe Zone Metric:** *{plat_specs['safe_zone']}*")
                st.markdown(f"🎯 **Strict Tonal Guardrail:** *{active_blueprint['tonal_guardrails']}*")

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
        # STEP 2: HARDENED BLUEPRINT COMPLIANT GENERATION
        # =====================================================================
        st.markdown("### 💡 Step 2: Playbook Synthesis Suggestion")
        
        if st.button(
            "✨ Generate Strategic Suggestion from Playbook", 
            use_container_width=True,
            help="Click to prompt Gemini to draft a high-fidelity copy outline rooted completely in your unique strategic persona."
        ):
            if not content_title:
                st.error("Please fill in an Asset Working Title to provide contextual fuel for generation.")
            elif not active_blueprint:
                st.error("No configuration guardrails found for this selection combination.")
            else:
                with st.spinner("Analyzing your Master Soul Guide and crafting blueprint-aligned copy..."):
                    try:
                        strategy_res = supabase.table("brand_strategy").select("soul_guide").eq("user_id", user_id).single().execute()
                        soul_guide_context = strategy_res.data.get("soul_guide", "") if strategy_res.data else ""
                        
                        if not soul_guide_context:
                            st.error("🚨 Master Soul Guide context not found. Please complete Phase 03: Illumination first.")
                            return

                        prompt = f"""
                        ROLE: Professional Brand Guardian & Master Strategic Copywriter.
                        TASK: Generate ready-to-publish raw copy for the asset title: '{content_title}'.
                        
                        CRITICAL FILTER: You must write purely from the user's specific perspective. Do NOT use, reference, or include the agency name 'Godzspeed' anywhere in your thought process, structural notes, or generated output copy.
                        
                        =======================================================================
                        🔥 HARD PLATFORM & ARCHITECTURAL LIMITS — YOU MUST COMPLY VERBATIM:
                        - CHANNEL PLATFORM: {selected_platform}
                        - STRICT MAXIMUM CHARACTER LIMIT: {plat_specs['char_max']} characters (Do NOT exceed under any circumstance)
                        - IDEAL TARGET RESOLUTION: {plat_specs['ideal_image']}
                        - TARGET MEDIUM FORMAT: {active_blueprint['medium_type']}
                        - TARGET DEPTH / LENGTH: {active_blueprint['target_length']}
                        - STRICT TONAL LAWS: {active_blueprint['tonal_guardrails']}
                        - MANDATORY STRUCTURAL RULES: {active_blueprint['structural_rules']}
                        =======================================================================
                        
                        CRITICAL COPYWRITING DIRECTIVE: You must structure the copy layout to conform to the formatting laws of {selected_platform}. For instance, if writing for Instagram or TikTok, keep layout structured for vertical readability with crisp pacing. Ensure the overall character volume sits safely below {plat_specs['char_max']}.
                        
                        MASTER PLAYBOOK PERSPECTIVE CONTEXT:
                        {soul_guide_context}
                        
                        OUTPUT: Provide only the fully-written copy block matching these parameters. Speak with poetic, commanding, elite 'hella smart' authority, focusing natively on strategic organizational communication, digital analytics frameworks, and marketing mix allocation model narratives. Do not append explanatory introductions or postscript commentary.
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

        # Dynamic live counter to monitor real-time character caps
        curr_len = len(edited_body)
        if curr_len > plat_specs['char_max']:
            st.error(f"❌ Platform Overflow: Current text spans `{curr_len:,}` characters. This breaks the structural limit of `{plat_specs['char_max']:,}` for {selected_platform}!")
        else:
            st.caption(f"📊 Volume Metrics: `{curr_len:,}` / `{plat_specs['char_max']:,}` allowed characters for {selected_platform}.")

        if st.session_state.workspace_text:
            user_feedback = st.chat_input("Ask the Guardian to rewrite, expand, or adjust tone parameters for this workspace...")
            if user_feedback:
                with st.spinner("Recalibrating asset against the corporate blueprint..."):
                    refine_prompt = f"""
                    ROLE: Professional Brand Guardian.
                    TASK: Revise the EXISTING TEXT based on the USER FEEDBACK. 
                    
                    STRICT PARAMETER CONSTRAINT REFERENCE:
                    - Keep tone strict: {active_blueprint['tonal_guardrails'] if active_blueprint else 'Professional'}
                    - Follow structural rules: {active_blueprint['structural_rules'] if active_blueprint else 'Standard'}
                    - Platform Maximum Limit: {plat_specs['char_max']} characters.
                    
                    CRITICAL CONSTRAINT: Absolutely do not use or output the word 'Godzspeed'.
                    EXISTING TEXT:\n{edited_body}
                    """
                    revised_text = get_soul_rebel_consultant(user_feedback, refine_prompt)
                    st.session_state.workspace_text = revised_text
                    st.session_state.guardian_rev += 1  
                    st.rerun()

        st.write("---")

        # =====================================================================
        # STEP 4: HARDENED COMPLIANCE SCAN MECHANISM WITH PLATFORM INTEGRATION RULES
        # =====================================================================
        st.markdown("### 🛡️ Step 4: Brand Alignment & Compliance Gate")
        
        c_col1, c_col2 = st.columns([1, 2])
        with c_col1:
            if st.button(
                "🔍 Run Brand Soul Alignment Scan", 
                use_container_width=True, 
                type="secondary",
                help="Triggers an AI-powered compliance sweep to audit your workspace copy against the core playbook tone rules."
            ):
                with st.spinner("Analyzing text for playbook alignment violations..."):
                    try:
                        strategy_res = supabase.table("brand_strategy").select("soul_guide").eq("user_id", user_id).single().execute()
                        soul_guide_context = strategy_res.data.get("soul_guide", "") if strategy_res.data else ""
                        
                        scan_prompt = f"""
                        ROLE: Strict Brand Identity & Technical Channel Auditor.
                        TASK: Audit the copy block against absolute tactical positioning metrics, channel blueprints, and platform parameters.
                        
                        HARD API LIMIT MANDATE:
                        The active platform selection is '{selected_platform}'. If the total character volume of the provided text (`{curr_len}`) exceeds the absolute maximum threshold of `{plat_specs['char_max']}`, you MUST immediately issue a hard FAIL. 
                        
                        THEMATIC ALIGNMENT ENFORCEMENT FILTER: 
                        The primary focus of this asset must remain tightly linked to corporate strategy, digital distribution pipelines, strategic media analysis, marketing execution metrics, or executive communication frameworks. 
                        If the asset working title or narrative text covers random consumer commodities, lifestyle hobbies, bicycles, or unaligned market sectors, you MUST immediately issue a hard fail standard on line 1. Do not bend rules or rationalize compliance for irrelevant topics unless a custom context applies.
                        
                        CRITICAL CONSTRAINT: Do not look for, reference, or mention the name 'Godzspeed'.
                        
                        AUDIT SCOPE:
                        - Asset Title Focus: '{content_title}'
                        - Platform Limits: {plat_specs['char_max']} chars Max | Resolution Standard: {plat_specs['ideal_image']}
                        - Tone Guide: {active_blueprint['tonal_guardrails']}
                        - Structural Demands: {active_blueprint['structural_rules']}
                        - Core Soul Guide: {soul_guide_context}
                        
                        TEXT TO AUDIT:
                        {edited_body}
                        
                        OUTPUT FORMAT RULES: You must return your analytical report matching this structure verbatim:
                        1. Your very first line must read exactly either 'SCORE: PASS' or 'SCORE: FAIL' based on thematic cohesion and stylistic adherence.
                        2. Follow with a markdown header titled '### 📊 Audit Breakdown Notes' and document bulleted structural parameters detailing any brand violations or pass justifications.
                        """
                        report = get_soul_rebel_consultant("Audit text", scan_prompt)
                        st.session_state.compliance_report = report
                        st.rerun()
                    except Exception as e:
                        st.error(f"Scan error: {e}")

        with c_col2:
            if st.session_state.compliance_report:
                report_text = st.session_state.compliance_report
                
                # Evaluate the strict first line formatting constraint
                first_line = report_text.split("\n")[0] if "\n" in report_text else report_text
                is_pass = "SCORE: PASS" in first_line or report_text.startswith("SCORE: PASS")
                
                if is_pass:
                    st.success("🎉 BRAND GUARDIAN AUDIT: PASSED")
                    st.info(report_text)
                else:
                    st.error("🚨 BRAND GUARDIAN AUDIT: FAILED COMPLIANCE")
                    st.info(report_text)
                    
                    # ADAPTIVE JUSTIFICATION OVERRIDE COMPONENT
                    st.write("---")
                    st.markdown("#### 🛠️ Campaign Justification Matrix")
                    st.caption("If this asset covers an off-brand CSR initiative, charity drive, or special project (e.g., a bicycle ride fundraiser), explain the business purpose below to override the core scope block.")
                    
                    justification_context = st.text_area(
                        "Strategic Override Reason / Context:",
                        placeholder="e.g., This is an annual charity bicycle ride campaign raising funds for municipal service initiatives, serving as our core corporate social responsibility rollout for Q3.",
                        key="guardian_override_reason_input"
                    )
                    
                    if st.button("🔥 Request Override Evaluation", use_container_width=True):
                        if not justification_context:
                            st.warning("Please type a strategic justification context to initiate an override scan.")
                        else:
                            with st.spinner("Re-auditing timeline asset with added context parameters..."):
                                try:
                                    strategy_res = supabase.table("brand_strategy").select("soul_guide").eq("user_id", user_id).single().execute()
                                    soul_guide_context = strategy_res.data.get("soul_guide", "") if strategy_res.data else ""
                                    
                                    override_prompt = f"""
                                    ROLE: Adaptive Brand Identity & Technical Channel Auditor.
                                    TASK: Re-evaluate the previously failed text asset, taking into account the user's explicit business justification and technical constraints.
                                    
                                    USER CAMPAIGN JUSTIFICATION/CONTEXT:
                                    {justification_context}
                                    
                                    If the user's justification frames this off-brand topic (like a bicycle ride) as a legitimate, approved corporate initiative, corporate responsibility fundraiser, or strategic community project, you are authorized to grant a 'SCORE: PASS' as long as the content sits under the hard platform character cap of `{plat_specs['char_max']}` and matches your core tone guide mechanics.
                                    
                                    AUDIT SCOPE:
                                    - Asset Title Focus: '{content_title}'
                                    - Hard API Limit: {plat_specs['char_max']} Max Chars
                                    - Tone Guide: {active_blueprint['tonal_guardrails']}
                                    - Structural Demands: {active_blueprint['structural_rules']}
                                    - Core Soul Guide: {soul_guide_context}
                                    
                                    TEXT TO AUDIT:
                                    {edited_body}
                                    
                                    OUTPUT FORMAT RULES:
                                    1. Your very first line must read exactly either 'SCORE: PASS' or 'SCORE: FAIL' based on style rules and this contextual justification exception.
                                    2. Follow with a markdown header titled '### 📊 Audit Breakdown Notes' detailing the override evaluation outcome.
                                    """
                                    override_report = get_soul_rebel_consultant("Override audit text", override_prompt)
                                    st.session_state.compliance_report = override