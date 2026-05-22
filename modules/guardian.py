import streamlit as st
import datetime
import time
import json
import re
from utils.gemini_ai import get_soul_rebel_consultant
from utils.supabase_db import supabase

# =====================================================================
# HARD PLATFORM API SPECIFICATIONS MATRIX
# =====================================================================
PLATFORM_LIMITS = {
    "Facebook": {"char_max": 5000, "ideal_image": "1080 x 1080 px", "aspect_ratio": "1:1"},
    "Instagram": {"char_max": 2200, "ideal_image": "1080 x 1350 px (4:5 Portrait)", "aspect_ratio": "4:5"},
    "LinkedIn": {"char_max": 3000, "ideal_image": "1200 x 1200 px", "aspect_ratio": "1:1"},
    "TikTok": {"char_max": 2200, "ideal_image": "1080 x 1920 px (9:16 Vertical)", "aspect_ratio": "9:16"},
    "Website Blog": {"char_max": 99999, "ideal_image": "1200 x 630 px", "aspect_ratio": "1.91:1"},
    "Substack Blog": {"char_max": 99999, "ideal_image": "1200 x 600 px", "aspect_ratio": "2:1"}
}

def load_blueprints():
    """Fetches strict content blueprints matrix dynamically from Supabase."""
    try:
        response = supabase.table("brand_content_blueprints").select("*").execute()
        return response.data if response.data else []
    except Exception as e:
        st.error(f"Error loading blueprints: {e}")
        return []

def load_content_calendar(user_id):
    """Fetches planned, drafted, and fully committed assets from database layers."""
    try:
        response = supabase.table("brand_content_items")\
            .select("*")\
            .eq("user_id", user_id)\
            .neq("title", "MASTER_CAMPAIGN_WORKSPACE")\
            .order("publish_date").execute()
        return response.data if response.data else []
    except Exception as e:
        st.error(f"Error pulling calendar entries: {e}")
        return []

def clean_display_text(architecture_text):
    """Removes backend payload blocks and scrubs any forbidden agency terms."""
    if not architecture_text:
        return ""
    text = re.sub(r"\[PILLARS_DATA_START\].*?\[PILLARS_DATA_END\]", "", architecture_text, flags=re.DOTALL).strip()
    text = re.sub(r"\bGodzspeed\b", "", text, flags=re.IGNORECASE)
    return text

def run(user_id):
    st.title("🛡️ The Brand Campaign & Guardian Control")
    st.caption("From High-Level Campaign Formulation to Hard Omni-Channel Compliance Audits.")
    st.write("---")

    # --- WORKSPACE STATE MANAGEMENT ---
    if "campaign_suggestion" not in st.session_state:
        st.session_state.campaign_suggestion = ""
    if "campaign_committed" not in st.session_state:
        st.session_state.campaign_committed = False
    if "committed_campaign_data" not in st.session_state:
        st.session_state.committed_campaign_data = {}
        
    if "active_content_suggestion" not in st.session_state:
        st.session_state.active_content_suggestion = ""
    if "workspace_text" not in st.session_state:
        st.session_state.workspace_text = ""
    if "compliance_report" not in st.session_state:
        st.session_state.compliance_report = None
    if "content_ready_for_scan" not in st.session_state:
        st.session_state.content_ready_for_scan = False
    if "guardian_rev" not in st.session_state:
        st.session_state.guardian_rev = 0

    # --- REHYDRATE ACTIVE DATABASE SESSION WORKSPACE ---
    blueprints = load_blueprints()
    soul_guide_context = ""
    try:
        strategy_res = supabase.table("brand_strategy").select("soul_guide").eq("user_id", user_id).single().execute()
        soul_guide_context = strategy_res.data.get("soul_guide", "") if strategy_res.data else ""
        soul_guide_context = re.sub(r"\bGodzspeed\b", "", soul_guide_context, flags=re.IGNORECASE)
        
        workspace_row = supabase.table("brand_content_items")\
            .select("*")\
            .eq("user_id", user_id)\
            .eq("title", "MASTER_CAMPAIGN_WORKSPACE")\
            .execute()
            
        if workspace_row.data:
            record = workspace_row.data[0]
            status_flag = record.get("status", "")
            
            if status_flag == "approved_for_publishing" and not st.session_state.campaign_committed:
                st.session_state.campaign_committed = True
                st.session_state.committed_campaign_data = {
                    "intent": clean_display_text(record.get("current_body", "")),
                    "architecture": clean_display_text(record.get("suggested_body", ""))
                }
            elif status_flag == "draft" and not st.session_state.campaign_suggestion:
                st.session_state.campaign_suggestion = clean_display_text(record.get("suggested_body", ""))
                if "init_intent_fallback" not in st.session_state:
                    st.session_state.init_intent_fallback = clean_display_text(record.get("current_body", ""))
    except Exception:
        pass

    # UI Splitting Matrix
    col_main, col_sidebar = st.columns([5, 2], gap="large")

    with col_main:
        # =====================================================================
        # STAGE 01: CAMPAIGN STRATEGIC DIRECTION
        # =====================================================================
        st.markdown("## 🎯 Stage 1: Campaign Strategic Direction")
        
        if not st.session_state.campaign_committed:
            fallback_text = st.session_state.get("init_intent_fallback", "")
            campaign_intent = st.text_area(
                "Describe your campaign objective or initiative purpose:",
                value=fallback_text,
                placeholder="e.g., We are organizing a charity campaign to raise money for municipal services...",
            )
            
            c_actions = st.columns([1, 1, 2])
            with c_actions[0]:
                if st.button("🔮 Brainstorm Strategy", use_container_width=True, type="primary"):
                    if not campaign_intent:
                        st.error("Please provide an initialization objective first.")
                    else:
                        with st.spinner("Formulating campaign strategy matrix..."):
                            prompt = f"""
                            ROLE: Independent Executive Consultant.
                            TASK: Take the user's specific campaign objective and structure it into a clean distribution framework.
                            
                            CRITICAL CONSTRAINT: You are ABSOLUTELY FORBIDDEN from using, referencing, or mentioning the name 'Godzspeed'. Write exclusively from the user's personal voice.
                            
                            USER'S EXACT CAMPAIGN OBJECTIVE: "{campaign_intent}"
                            USER'S APPROVED SOUL GUIDE INTEL CONTEXT: {soul_guide_context}
                            
                            OUTPUT FORMAT: Present the structured framework matching these headers:
                            ### 📋 Executive Summary
                            ### 🗂️ Activated Brand Pillars
                            ### 📱 Recommended Distribution Channels
                            """
                            suggestion_output = get_soul_rebel_consultant("Draft Campaign Framework", prompt)
                            suggestion_output = clean_display_text(suggestion_output)
                            
                            sync_payload = {
                                "user_id": user_id, "title": "MASTER_CAMPAIGN_WORKSPACE",
                                "current_body": campaign_intent, "suggested_body": suggestion_output,
                                "status": "draft", "category": "CAMPAIGN_SYSTEM",
                                "platform": "SYSTEM_WORKBENCH", "publish_date": str(datetime.date.today())
                            }
                            try:
                                check_row = supabase.table("brand_content_items").select("id").eq("user_id", user_id).eq("title", "MASTER_CAMPAIGN_WORKSPACE").execute()
                                if check_row.data:
                                    supabase.table("brand_content_items").update(sync_payload).eq("id", check_row.data[0]["id"]).execute()
                                else:
                                    supabase.table("brand_content_items").insert(sync_payload).execute()
                            except Exception:
                                pass

                            st.session_state.campaign_suggestion = suggestion_output
                            st.session_state.init_intent_fallback = campaign_intent
                            st.rerun()
            
            with c_actions[1]:
                if st.button("🔄 Reset Campaign", use_container_width=True):
                    try:
                        supabase.table("brand_content_items").delete().eq("user_id", user_id).eq("title", "MASTER_CAMPAIGN_WORKSPACE").execute()
                    except Exception:
                        pass
                    st.session_state.campaign_suggestion = ""
                    if "init_intent_fallback" in st.session_state:
                        del st.session_state.init_intent_fallback
                    st.rerun()

            if st.session_state.campaign_suggestion:
                st.info("### 📋 Recommended Campaign Architecture Matrix")
                st.write(st.session_state.campaign_suggestion)
                
                if st.button("🔥 Commit Strategy & Unlock Content Creation", use_container_width=True, type="primary"):
                    commit_payload = {
                        "user_id": user_id, "title": "MASTER_CAMPAIGN_WORKSPACE",
                        "current_body": campaign_intent, "suggested_body": st.session_state.campaign_suggestion,
                        "status": "approved_for_publishing", "category": "CAMPAIGN_SYSTEM",
                        "platform": "SYSTEM_WORKBENCH", "publish_date": str(datetime.date.today())
                    }
                    try:
                        check_row = supabase.table("brand_content_items").select("id").eq("user_id", user_id).eq("title", "MASTER_CAMPAIGN_WORKSPACE").execute()
                        if check_row.data:
                            supabase.table("brand_content_items").update(commit_payload).eq("id", check_row.data[0]["id"]).execute()
                        else:
                            supabase.table("brand_content_items").insert(commit_payload).execute()
                    except Exception:
                        pass
                        
                    st.session_state.campaign_committed = True
                    st.session_state.committed_campaign_data = {
                        "intent": campaign_intent,
                        "architecture": st.session_state.campaign_suggestion
                    }
                    st.success("Strategic direction locked down and saved!")
                    time.sleep(1.0)
                    st.rerun()
        else:
            st.success("✅ Campaign Strategy Committed & Locked Into Memory.")
            with st.expander("View Active Campaign Strategic Parameters"):
                st.write(st.session_state.committed_campaign_data.get("architecture", ""))
            if st.button("🗑️ Scrap Strategy & Restart Campaign", type="secondary"):
                try:
                    supabase.table("brand_content_items").delete().eq("user_id", user_id).eq("title", "MASTER_CAMPAIGN_WORKSPACE").execute()
                except Exception:
                    pass
                st.session_state.campaign_committed = False
                st.session_state.campaign_suggestion = ""
                st.session_state.committed_campaign_data = {}
                st.session_state.workspace_text = ""
                st.session_state.active_content_suggestion = ""
                st.session_state.compliance_report = None
                if "init_intent_fallback" in st.session_state:
                    del st.session_state.init_intent_fallback
                st.rerun()

        st.write("---")

        # =====================================================================
        # STAGE 02: PURE BLUEPRINT CONTENT GENERATION ENGINE
        # =====================================================================
        st.markdown("## 📝 Stage 2: Content Generation & Blueprint Tailoring")
        
        if not st.session_state.campaign_committed:
            st.caption("🔒 *Commit to a campaign strategy above to unlock the asset generation terminal.*")
        elif not blueprints:
            st.error("⚠️ No blueprints found in table 'brand_content_blueprints'.")
        else:
            available_categories = list(set([bp['category'] for bp in blueprints]))
            
            g_col1, g_col2 = st.columns(2)
            with g_col1:
                chosen_pillar = st.selectbox("Active Brand Blueprint Category / Pillar:", available_categories)
            
            filtered_platforms = [bp['platform'] for bp in blueprints if bp['category'] == chosen_pillar]
            with g_col2:
                chosen_channel = st.selectbox("Target Publishing Platform / Channel:", filtered_platforms if filtered_platforms else list(PLATFORM_LIMITS.keys()))
            
            active_blueprint = next((bp for bp in blueprints if bp['category'] == chosen_pillar and bp['platform'] == chosen_channel), None)
            active_specs = PLATFORM_LIMITS.get(chosen_channel, {"char_max": 3000, "ideal_image": "1080x1080", "aspect_ratio": "1:1"})
            
            if active_blueprint:
                with st.expander("🔍 Active Blueprint Guardrails (Live from Database)", expanded=True):
                    st.markdown(f"**Format:** `{active_blueprint.get('medium_type', 'Standard')}` | **Target Length:** `{active_blueprint.get('target_length', 'Variable')}` | **Max Limit:** `{active_specs['char_max']:,}` chars")
                    st.markdown(f"**Tonal Guardrails:** *{active_blueprint.get('tonal_guardrails', 'None')}*")
                    st.markdown(f"**Structural Rules:** *{active_blueprint.get('structural_rules', 'None')}*")

            content_title = st.text_input("Asset Working Title:", placeholder="e.g., Special Announcement: Help Us Make an Impact")
            publish_date = st.date_input("Target Publishing Window Date:", datetime.date.today())

            # FIXED: NEW INJECTED USER DIRECTIVE FIELD FOR HIGH-FIDELITY COPY CONTROL
            custom_generation_prompt = st.text_area(
                "Specific Copywriting Instructions for this piece (Optional Guide Rails):",
                placeholder="e.g., Write a high-urgency email blast asking our contacts to register or donate right now. Keep it direct and emotional...",
                help="Type exactly what you want this specific piece of content to focus on, and the engine will build the copy based directly on your instructions."
            )

            st.write(" ")
            
            # --- GENERATION WORKFLOW ACTIONS ---
            g_buttons = st.columns(2)
            with g_buttons[0]:
                if st.button("✨ Draft Custom Copy Suggestion", use_container_width=True, type="primary"):
                    if not content_title:
                        st.error("Provide a working title headline to fuel the generation parameters.")
                    elif not active_blueprint:
                        st.error("Missing selected blueprint matching key paths.")
                    else:
                        with st.spinner("Generating raw platform content asset copy..."):
                            
                            # Build the dynamic user command block if provided
                            user_instruction_block = ""
                            if custom_generation_prompt:
                                user_instruction_block = f"""
                                =======================================================================
                                🚨 CRITICAL USER OPERATIONAL INSTRUCTIONS:
                                You MUST directly prioritize and fulfill these copywriting requirements:
                                "{custom_generation_prompt}"
                                =======================================================================
                                """

                            prompt = f"""
                            ROLE: Expert Direct-Response Copywriter.
                            TASK: Write the final, ready-to-publish raw body text for an asset titled: '{content_title}'.
                            
                            🚨 ABSOLUTELY UNYIELDING MASTER CONTENT LAW:
                            - You must ONLY write and return the literal, deployable copy block for the channel '{chosen_channel}'.
                            - Do NOT output strategic outlines, introductory remarks, summaries, placeholder advice, meta commentary, notes, or execution tips. 
                            - Dive straight into the copy text immediately. If the target channel is an Email Blast, write the full cohesive email body. If it is a Facebook or LinkedIn post, output only the actual post caption copy with text hooks and matching formatting.
                            
                            {user_instruction_block}
                            
                            🚨 ABSOLUTELY FORBIDDEN LABELS:
                            - Never print, reference, or output the word 'Godzspeed'. Write from the individual user's perspective.
                            
                            🚨 STRICT LENGTH CAPS:
                            Your output copy block text MUST be strictly below {active_specs['char_max']} total characters. Keep it concise.
                            
                            ACTIVE CAMPAIGN FRAMEWORK UNDERLAY:
                            {st.session_state.committed_campaign_data.get('architecture')}
                            
                            USER'S INITIAL CAMPAIGN INTENT:
                            "{st.session_state.committed_campaign_data.get('intent')}"
                            
                            BLUEPRINT PARAMETER GUARDRAILS:
                            - PILLAR CATEGORY: {chosen_pillar}
                            - PLATFORM/CHANNEL: {chosen_channel}
                            - FORMAT STRUCTURE: {active_blueprint.get('medium_type')}
                            - TONAL GUARDRAILS: {active_blueprint.get('tonal_guardrails')}
                            - STRUCTURAL RULES: {active_blueprint.get('structural_rules')}
                            - STRATEGIC SOUL GUIDE CONTEXT: {soul_guide_context}
                            
                            OUTPUT VERBATIM SPECIFICATION: Return ONLY the raw deployable copy block text now. No commentary, no headings, no chit-chat.
                            """
                            raw_out = get_soul_rebel_consultant("Draft Content Piece", prompt)
                            st.session_state.active_content_suggestion = clean_display_text(raw_out)
                            st.rerun()
            with g_buttons[1]:
                if st.button("❌ Clear & Restart Draft", use_container_width=True):
                    st.session_state.active_content_suggestion = ""
                    st.session_state.workspace_text = ""
                    st.session_state.compliance_report = None
                    st.session_state.content_ready_for_scan = False
                    st.rerun()

            if st.session_state.active_content_suggestion:
                st.markdown("### 🤖 Guardian Copy Suggestion Outbox")
                st.info(st.session_state.active_content_suggestion)
                
                if st.button("✅ Transfer Suggestion to Active Workspace", use_container_width=True):
                    raw_suggestion = st.session_state.active_content_suggestion
                    if len(raw_suggestion) > active_specs['char_max']:
                        st.session_state.workspace_text = raw_suggestion[:active_specs['char_max']]
                        st.warning(f"✂️ The generated copy was automatically sliced to fit the absolute {active_specs['char_max']} character ceiling.")
                    else:
                        st.session_state.workspace_text = raw_suggestion
                        
                    st.session_state.active_content_suggestion = ""
                    st.rerun()

            # --- EDITING CANVAS ---
            st.write(" ")
            w_key = f"workspace_rev_layer_{st.session_state.guardian_rev}"
            edited_body = st.text_area(
                "Active Composition Canvas:",
                value=st.session_state.workspace_text,
                height=300,
                key=w_key,
                help="Refine your raw copy body text blocks here."
            )
            st.session_state.workspace_text = re.sub(r"\bGodzspeed\b", "", edited_body, flags=re.IGNORECASE)

            c_length = len(st.session_state.workspace_text)
            if c_length > active_specs['char_max']:
                st.error(f"⚠️ Platform Overflow: Copy scales to `{c_length}` characters. This breaks the hard `{active_specs['char_max']}` threshold for {chosen_channel}!")
            else:
                st.caption(f"Volume Tracker: `{c_length}` / `{active_specs['char_max']}` maximum characters for {chosen_channel}.")

            if st.session_state.workspace_text:
                chat_feedback = st.chat_input("Ask the controller to rewrite, extend, or trim this text...")
                if chat_feedback:
                    with st.spinner("Refining asset text body..."):
                        refine_prompt = f"""
                        TASK: Revise the copy text based on user directions. Ensure text bounds fit rules for {chosen_channel}.
                        🚨 AUTOMATIC TRUNCATION METRIC: You MUST compress the output to sit completely beneath {active_specs['char_max']} characters. Avoid advisory statements or summaries; return ONLY raw draft text.
                        CRITICAL CONSTRAINT: Focus strictly on the core theme. Do not use the word 'Godzspeed'.
                        EXISTING BODY LAYOUT:\n{st.session_state.workspace_text}
                        """
                        refined_output = get_soul_rebel_consultant(chat_feedback, refine_prompt)
                        refined_output = clean_display_text(refined_output)
                        
                        if len(refined_output) > active_specs['char_max']:
                            st.session_state.workspace_text = refined_output[:active_specs['char_max']]
                        else:
                            st.session_state.workspace_text = refined_output
                            
                        st.session_state.guardian_rev += 1
                        st.rerun()

                if st.button("🔒 Lock Workspace & Proceed to Compliance Scan", use_container_width=True):
                    st.session_state.content_ready_for_scan = True
                    st.success("Workspace locked. Stage 3 Compliance Gate is now authorized to run.")
                    st.rerun()

        st.write("---")

        # =====================================================================
        # STAGE 03: HARD COMPLIANCE AUDIT GATE
        # =====================================================================
        st.markdown("## 🛡️ Stage 3: Brand Guardian Compliance Gate")
        
        if not st.session_state.content_ready_for_scan:
            st.caption("🔒 *Complete your workspace composition steps above and lock down composition to clear the compliance pathways.*")
        else:
            st.warning(f"**Target System Rule Check:** Auditing copy against {chosen_channel} blueprint rules.")
            
            if st.button("🔍 Execute Brand Soul Alignment Scan", use_container_width=True, type="primary"):
                with st.spinner("Auditing thematic lines against active playbook rules..."):
                    scan_prompt = f"""
                    ROLE: Strict Independent Identity & Channel Integrity Sweeper.
                    TASK: Audit this text copy against absolute architectural limits, active database blueprints, and user campaign directives.
                    
                    CRITICAL COMPLIANCE FILTER: Verify that this copy matches the user's committed campaign focus topic perfectly. If it drifts, FAIL it.
                    HARD PLATFORM CONSTRAINT MANDATE: If the character volume (`{c_length}`) exceeds `{active_specs['char_max']}`, FAIL it.
                    🚨 CRITICAL CONSTRAINT: Absolutely do not look for, mention, or print the name 'Godzspeed'. If it appears, fail the audit immediately.
                    
                    📐 BRAND CONTENT BLUEPRINT LAWS TO AUDIT AGAINST:
                    - MATRIC CATEGORY: {chosen_pillar}
                    - CHANNEL FORMAT: {chosen_channel}
                    - TONAL LAWS DETECTED: {active_blueprint.get('tonal_guardrails') if active_blueprint else 'None'}
                    - STRUCTURAL RULES DETECTED: {active_blueprint.get('structural_rules') if active_blueprint else 'None'}
                    
                    LOCKED CAMPAIGN BLUEPRINT ARCHITECTURE: {st.session_state.committed_campaign_data.get('architecture')}
                    CORE SYSTEM APPROVED BRAND GUIDE CONTEXT: {soul_guide_context}
                    
                    TEXT TO AUDIT:
                    {st.session_state.workspace_text}
                    
                    OUTPUT LAYOUT FORMAT RULES: Your return sequence parameters must match this format structure:
                    Line 1 must contain exactly either 'SCORE: PASS' or 'SCORE: FAIL'.
                    Follow with a markdown heading titled '### 📊 Compliance Diagnostic Summary Notes' and outline structural breakdowns explaining the positioning or character-count violation reasons.
                    """
                    audit_res = get_soul_rebel_consultant("Verify Asset Integrity", scan_prompt)
                    st.session_state.compliance_report = re.sub(r"\bGodzspeed\b", "[CENSORED]", audit_res, flags=re.IGNORECASE)
                    st.rerun()

            if st.session_state.compliance_report:
                report_string = st.session_state.compliance_report
                first_line = report_string.split("\n")[0] if "\n" in report_string else report_string
                is_pass = "SCORE: PASS" in first_line or report_string.startswith("SCORE: PASS")
                
                if is_pass:
                    st.success("🎉 BRAND GUARDIAN GATEKEEPER: POSITIONING MATRIX CLEARED (PASSED)")
                    st.info(report_string)
                else:
                    st.error("🚨 BRAND GUARDIAN GATEKEEPER: COMPLIANCE INTEGRITY THREAT DETECTED (FAILED)")
                    st.info(report_string)

                st.write(" ")
                st.markdown("### 💾 Step 4: Pipeline Target Commit Routing")
                
                payload = {
                    "user_id": user_id, "title": content_title,
                    "suggested_body": st.session_state.active_content_suggestion, "current_body": st.session_state.workspace_text,
                    "category": chosen_pillar, "platform": chosen_channel,
                    "publish_date": str(publish_date), "guardian_notes": report_string
                }

                p_buttons = st.columns(2)
                with p_buttons[0]:
                    if st.button("💾 Save Progress as Draft Room Item", use_container_width=True):
                        with st.spinner("Pushing metrics to database lines..."):
                            payload["status"] = "draft"
                            exist_check = supabase.table("brand_content_items").select("id").eq("user_id", user_id).eq("title", content_title).eq("platform", chosen_channel).eq("publish_date", str(publish_date)).execute()
                            if exist_check.data:
                                supabase.table("brand_content_items").update(payload).eq("id", exist_check.data[0]["id"]).execute()
                            else:
                                supabase.table("brand_content_items").insert(payload).execute()
                            
                            st.success("Draft saved successfully!")
                            time.sleep(1)
                            st.rerun()
                with p_buttons[1]:
                    if st.button("🚀 Approve & Lock for Publication Rollout", use_container_width=True, type="primary", disabled=not is_pass):
                        with st.spinner("Locking validated asset to calendar matrix..."):
                            payload["status"] = "approved_for_publishing"
                            exist_check = supabase.table("brand_content_items").select("id").eq("user_id", user_id).eq("title", content_title).eq("platform", chosen_channel).eq("publish_date", str(publish_date)).execute()
                            if exist_check.data:
                                supabase.table("brand_content_items").update(payload).eq("id", exist_check.data[0]["id"]).execute()
                            else:
                                supabase.table("brand_content_items").insert(payload).execute()
                            
                            st.session_state.active_content_suggestion = ""
                            st.session_state.workspace_text = ""
                            st.session_state.compliance_report = None
                            st.session_state.content_ready_for_scan = False
                            st.success("Asset pushed to live operational schedule timeline!")
                            time.sleep(1)
                            st.rerun()

    # =====================================================================
    # RIGHT SIDEBAR TIMELINE ENGINE
    # =====================================================================
    with col_sidebar:
        st.markdown("### 📅 Active Production Timelines")
        st.caption("Manage or re-edit items within your strategy stream.")
        st.write("---")
        
        calendar_data = load_content_calendar(user_id)
        
        if not calendar_data:
            st.info("Your tactical rollout timeline pipeline is currently empty.")
        else:
            st.markdown("#### 🚀 Scheduled for Release")
            approved_items = [i for i in calendar_data if i['status'] == 'approved_for_publishing']
            if not approved_items:
                st.caption("No assets currently locked for deployment loops.")
            for item in approved_items:
                with st.container(border=True):
                    st.markdown(f"**🟢 {item['title']}**")
                    st.caption(f"📅 **Rollout:** {item['publish_date']} | 📱 **Platform:** {item['platform']}")
                    
                    with st.expander("Review Confirmed Copy"):
                        st.code(item['current_body'])
                        st.write(" ")
                        
                        m1, m2 = st.columns(2)
                        with m1:
                            if st.button("↩️ Re-Edit", key=f"revert_pub_{item['id']}", use_container_width=True):
                                supabase.table("brand_content_items").update({"status": "draft"}).eq("id", item['id']).execute()
                                st.session_state.campaign_committed = True
                                st.session_state.override_cat = item['category']
                                st.session_state.override_plat = item['platform']
                                st.session_state.override_title = item['title']
                                st.session_state.override_date = datetime.datetime.strptime(item['publish_date'], "%Y-%m-%d").date()
                                st.session_state.workspace_text = item['current_body']
                                st.session_state.compliance_report = None  
                                st.session_state.content_ready_for_scan = False
                                st.session_state.guardian_rev += 1
                                st.rerun()
                        with m2:
                            if st.button("🗑️ Delete", key=f"del_pub_{item['id']}", use_container_width=True):
                                supabase.table("brand_content_items").delete().eq("id", item['id']).execute()
                                st.rerun()

            st.write(" ")
            st.markdown("#### 📝 Workspace Vault Drafts")
            draft_items = [i for i in calendar_data if i['status'] == 'draft']
            if not draft_items:
                st.caption("No work-in-progress drafts sitting inside repository tracks.")
            for item in draft_items:
                with st.container(border=True):
                    st.markdown(f"**🗂️ {item['title']}**")
                    st.caption(f"📅 **Target:** {item['publish_date']} | 🛠️ **Platform:** {item['platform']}")
                    
                    d_actions = st.columns(2)
                    with d_actions[0]:
                        if st.button("📂 Load & Edit", key=f"load_draft_item_{item['id']}", use_container_width=True):
                            st.session_state.campaign_committed = True
                            st.session_state.override_cat = item['category']
                            st.session_state.override_plat = item['platform']
                            st.session_state.override_title = item['title']
                            st.session_state.override_date = datetime.datetime.strptime(item['publish_date'], "%Y-%m-%d").date()
                            st.session_state.workspace_text = item['current_body']
                            st.session_state.active_content_suggestion = item['suggested_body'] or ""
                            st.session_state.compliance_report = item['guardian_notes']
                            st.session_state.content_ready_for_scan = True if item['guardian_notes'] else False
                            st.session_state.guardian_rev += 1
                            st.rerun()
                    with d_actions[1]:
                        if st.button("🗑️ Delete Draft", key=f"del_draft_item_{item['id']}", use_container_width=True):
                            supabase.table("brand_content_items").delete().eq("id", item['id']).execute()
                            st.rerun()