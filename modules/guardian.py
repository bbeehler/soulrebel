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

def invalidate_previous_compliance_scan():
    """Wipes previous audit reports instantly when user text changes are detected."""
    st.session_state.compliance_report = None
    st.session_state.content_ready_for_scan = False

@st.dialog("📋 Review Confirmed Asset Copy", width="large")
def show_review_modal(item_title, item_body):
    """Renders a clean, centered overlay window to safely inspect published copy scripts."""
    st.markdown(f"### {item_title}")
    st.caption("This copy block is locked and scheduled for publication deployment loops.")
    st.write("---")
    st.code(item_body, language="text")
    st.write(" ")
    if st.button("Close Viewer", use_container_width=True):
        st.rerun()

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

    # --- FIXED: ADDED METADATA TRACKERS FOR UI HYDRATION & DB SYNC ---
    if "active_item_id" not in st.session_state:
        st.session_state.active_item_id = None
    if "active_title" not in st.session_state:
        st.session_state.active_title = ""
    if "active_category" not in st.session_state:
        st.session_state.active_category = None
    if "active_platform" not in st.session_state:
        st.session_state.active_platform = None
    if "active_date" not in st.session_state:
        st.session_state.active_date = datetime.date.today()

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
                            ROLE: Independent Executive Consultant & Chief Marketing Architect.
                            TASK: Take the user's specific campaign objective and structure it into a clean distribution framework.
                            
                            🚨 CRITICAL CONSTRAINTS:
                            - Write purely, directly, and exclusively from the individual user's personal voice.
                            - You are ABSOLUTELY FORBIDDEN from using, referencing, naming, or mentioning the agency name 'Godzspeed' or any outside marketing agency entity anywhere in your text.
                            - Ground all insights entirely within the provided Master Soul Guide document.
                            - You must ONLY use, frame, and structure the exact core topic, objective, and campaign idea specified by the user below.
                            - Do NOT expand, hallucinate, or generalize beyond what the user wrote.
                            
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
                    st.success("Strategic direction locked down and initialized smoothly!")
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
            
            is_locked_for_review = st.session_state.content_ready_for_scan
            
            # FIXED: Synced UI Fields with loaded data state handlers
            g_col1, g_col2 = st.columns(2)
            with g_col1:
                cat_index = available_categories.index(st.session_state.active_category) if st.session_state.active_category in available_categories else 0
                chosen_pillar = st.selectbox("Active Brand Blueprint Category / Pillar:", available_categories, index=cat_index, disabled=is_locked_for_review)
                st.session_state.active_category = chosen_pillar
            
            filtered_platforms = [bp['platform'] for bp in blueprints if bp['category'] == chosen_pillar]
            with g_col2:
                plat_index = filtered_platforms.index(st.session_state.active_platform) if st.session_state.active_platform in filtered_platforms else 0
                chosen_channel = st.selectbox("Target Publishing Platform / Channel:", filtered_platforms if filtered_platforms else list(PLATFORM_LIMITS.keys()), index=plat_index, disabled=is_locked_for_review)
                st.session_state.active_platform = chosen_channel
            
            active_blueprint = next((bp for bp in blueprints if bp['category'] == chosen_pillar and bp['platform'] == chosen_channel), None)
            active_specs = PLATFORM_LIMITS.get(chosen_channel, {"char_max": 3000, "ideal_image": "1080x1080", "aspect_ratio": "1:1"})
            
            if active_blueprint:
                with st.expander("🔍 Active Blueprint Guardrails (Live from Database)", expanded=True):
                    st.markdown(f"**Format:** `{active_blueprint.get('medium_type', 'Standard')}` | **Target Length:** `{active_blueprint.get('target_length', 'Variable')}` | **Max Limit:** `{active_specs['char_max']:,}` chars")
                    st.markdown(f"**Tonal Guardrails:** *{active_blueprint.get('tonal_guardrails', 'None')}*")
                    st.markdown(f"**Structural Rules:** *{active_blueprint.get('structural_rules', 'None')}*")

            content_title = st.text_input("Asset Working Title:", value=st.session_state.active_title, placeholder="e.g., Special Announcement: Help Us Make an Impact", disabled=is_locked_for_review)
            st.session_state.active_title = content_title
            
            publish_date = st.date_input("Target Publishing Window Date:", value=st.session_state.active_date, disabled=is_locked_for_review)
            st.session_state.active_date = publish_date

            custom_generation_prompt = st.text_area(
                "Specific Copywriting Instructions for this piece (Optional Guide Rails):",
                placeholder="e.g., Write a high-urgency email blast asking our contacts to register or donate right now...",
                disabled=is_locked_for_review
            )

            st.write(" ")
            
            # --- GENERATION WORKFLOW ACTIONS ---
            g_buttons = st.columns(2)
            with g_buttons[0]:
                if st.button("✨ Draft Custom Copy Suggestion", use_container_width=True, type="primary", disabled=is_locked_for_review):
                    if not content_title:
                        st.error("Provide a working title headline to fuel the generation parameters.")
                    elif not active_blueprint:
                        st.error("Missing selected blueprint matching key paths.")
                    else:
                        with st.spinner("Generating raw platform content asset copy..."):
                            user_instruction_block = ""
                            if custom_generation_prompt:
                                user_instruction_block = f"""
                                =======================================================================
                                🔥 PRIMARY DIRECTIVE FROM USER 🔥
                                Focus your writing entirely on executing this specific request:
                                "{custom_generation_prompt}"
                                =======================================================================
                                """

                            prompt = f"""
                            ROLE: You are an expert Ghostwriter and Direct-Response Copywriter.
                            TASK: Write the final, ready-to-publish raw copy for a '{chosen_channel}' asset titled '{content_title}'.

                            --- STEP 1: BACKGROUND CONTEXT ---
                            (Read and absorb this to understand the goal and tone, but DO NOT mimic its structure. Do not output strategy headers or bullet points).
                            Campaign Intent: {st.session_state.committed_campaign_data.get('intent')}
                            Campaign Strategy Context: {st.session_state.committed_campaign_data.get('architecture')}
                            Brand Identity Guide: {soul_guide_context}
                            
                            --- STEP 2: CHANNEL RULES ---
                            Platform: {chosen_channel}
                            Format Requirement: {active_blueprint.get('medium_type')}
                            Tonal Directives: {active_blueprint.get('tonal_guardrails')}
                            Structural Rules: {active_blueprint.get('structural_rules')}
                            Maximum Length: {active_specs['char_max']} characters.

                            --- STEP 3: YOUR SPECIFIC INSTRUCTIONS FOR THIS ASSET ---
                            {user_instruction_block if custom_generation_prompt else "Write highly engaging, conversion-focused copy for this channel based on the campaign intent."}

                            --- STRICT OUTPUT RULES ---
                            1. Output ONLY the raw copy text. Start writing immediately.
                            2. NO introductory phrases (e.g., "Here is the copy:").
                            3. NO strategic summaries, outlines, notes, or commentary.
                            4. If this is an email, write the subject line and then the body. If it is a social post, write the exact caption.
                            5. NEVER output or reference the word 'Godzspeed'.
                            
                            START DRAFT COPY NOW:
                            """
                            raw_out = get_soul_rebel_consultant("Draft Content Piece", prompt)
                            st.session_state.active_content_suggestion = clean_display_text(raw_out)
                            st.rerun()
            with g_buttons[1]:
                if st.button("❌ Clear & Restart Draft", use_container_width=True):
                    st.session_state.active_item_id = None
                    st.session_state.active_title = ""
                    st.session_state.active_date = datetime.date.today()
                    st.session_state.active_content_suggestion = ""
                    st.session_state.workspace_text = ""
                    st.session_state.guardian_rev += 1
                    st.session_state.compliance_report = None
                    st.session_state.content_ready_for_scan = False
                    st.rerun()

            if st.session_state.active_content_suggestion:
                st.markdown("### 🤖 Guardian Copy Suggestion Outbox")
                st.info(st.session_state.active_content_suggestion)
                
                if st.button("✅ Transfer Suggestion to Active Workspace", use_container_width=True):
                    raw_suggestion = st.session_state.active_content_suggestion
                    if len(raw_suggestion) > active_specs['char_max']:
                        final_text = raw_suggestion[:active_specs['char_max']]
                        st.warning(f"✂️ The copy was automatically sliced to fit the {active_specs['char_max']} limit.")
                    else:
                        final_text = raw_suggestion
                    
                    st.session_state.workspace_text = final_text
                    st.session_state["guardian_workspace_canvas_field_" + str(st.session_state.guardian_rev)] = final_text
                    st.session_state.active_content_suggestion = ""
                    invalidate_previous_compliance_scan()
                    st.rerun()

            # --- EDITING CANVAS ---
            st.write(" ")
            w_key = f"guardian_workspace_canvas_field_{st.session_state.guardian_rev}"
            
            edited_body = st.text_area(
                "Active Composition Canvas:",
                value=st.session_state.workspace_text,
                height=300,
                key=w_key,
                on_change=invalidate_previous_compliance_scan,
                disabled=is_locked_for_review,
                help="Refine your raw copy body text blocks here."
            )
            
            st.session_state.workspace_text = re.sub(r"\bGodzspeed\b", "", edited_body, flags=re.IGNORECASE)

            c_length = len(st.session_state.workspace_text)
            if c_length > active_specs['char_max']:
                st.error(f"⚠️ Platform Overflow: `{c_length}` / `{active_specs['char_max']}` chars!")
            else:
                st.caption(f"Volume Tracker: `{c_length}` / `{active_specs['char_max']}` characters.")

            if st.session_state.workspace_text and not is_locked_for_review:
                chat_feedback = st.chat_input("Ask the controller to rewrite, extend, or trim this text...")
                if chat_feedback:
                    with st.spinner("Refining asset text body..."):
                        refine_prompt = f"""
                        You are a copywriter making direct revisions to a draft.
                        
                        USER'S REVISION INSTRUCTION: "{chat_feedback}"
                        
                        CURRENT DRAFT TO REVISE:
                        {st.session_state.workspace_text}
                        
                        RULES:
                        1. Apply the user's feedback to the text.
                        2. Output ONLY the new, revised raw text. NO explanations. NO "Here is the updated version".
                        3. MUST be under {active_specs['char_max']} characters.
                        4. NEVER output the word 'Godzspeed'.
                        """
                        refined_output = get_soul_rebel_consultant(chat_feedback, refine_prompt)
                        refined_output = clean_display_text(refined_output)
                        
                        if len(refined_output) > active_specs['char_max']:
                            refined_output = refined_output[:active_specs['char_max']]
                            
                        st.session_state.workspace_text = refined_output
                        st.session_state.guardian_rev += 1
                        invalidate_previous_compliance_scan()
                        st.rerun()

                if st.button("🔒 Lock Workspace & Proceed to Compliance Scan", use_container_width=True, disabled=(c_length == 0 or c_length > active_specs['char_max'])):
                    st.session_state.content_ready_for_scan = True
                    st.success("Workspace locked. Stage 3 Compliance Gate is now authorized.")
                    st.rerun()
            elif is_locked_for_review:
                if st.button("🔓 Unlock Workspace to Make Adjustments", use_container_width=True):
                    st.session_state.content_ready_for_scan = False
                    st.session_state.compliance_report = None
                    st.rerun()

        st.write("---")

	# =====================================================================
        # STAGE 03: HARD COMPLIANCE AUDIT GATE
        # =====================================================================
        st.markdown("## 🛡️ Stage 3: Brand Guardian Compliance Gate")
        
        if not st.session_state.content_ready_for_scan:
            st.caption("🔒 *Complete your workspace composition steps above and lock down composition to clear the compliance pathways.*")
        else:
            st.warning(f"**Target System Rule Check:** Auditing copy against {chosen_channel} rules.")
            
            if st.button("🔍 Execute Brand Soul Alignment Scan", use_container_width=True, type="primary"):
                with st.spinner("Auditing thematic lines against active playbook rules..."):
                    
                    # HARD OVERRULE PROMPT: Strips out strategist personas completely
                    scan_prompt = f"""
                    SYSTEM PERSONA: You are a strict Proofreader and Tone Copy Editor. You are NOT a marketing consultant, strategist, or planner. Do not give business advice, do not create frameworks, and do not summarize goals.

                    TASK: Analyze the following copy block against two rigid rules.
                    
                    CRITICAL CONSTRAINT: 
                    Do not print, mention, or look for the word 'Godzspeed'. If it appears, fail the audit instantly.

                    RULE 1 - TONAL GUARDRAILS: {active_blueprint.get('tonal_guardrails', 'Authoritative and clean presentation')}
                    RULE 2 - STRUCTURAL CONSTRAINTS: {active_blueprint.get('structural_rules', 'Direct presentation copy layout')}

                    ===================================================================
                    EXACT TEXT COPY TO EDIT:
                    "{st.session_state.workspace_text}"
                    ===================================================================

                    OUTPUT FORMAT MATRIX (YOU MUST FOLLOW THIS EXACTLY):
                    Line 1 MUST be exactly one of these two phrases:
                    SCORE: PASS
                    - OR -
                    SCORE: FAIL

                    If the text is 'SCORE: FAIL', you must list exactly 1 to 3 bullet points explaining precisely WHICH sentence or word broke the tonal rules, WHAT makes it incorrect for the platform '{chosen_channel}', and exactly HOW to rewrite that specific line to fix it. 

                    No intro, no strategic advice, no marketing tips. Start directly with the score.
                    """
                    audit_res = get_soul_rebel_consultant("Verify Asset Integrity", scan_prompt)
                    st.session_state.compliance_report = re.sub(r"\bGodzspeed\b", "[CENSORED]", audit_res, flags=re.IGNORECASE)
                    st.rerun()

            if st.session_state.compliance_report:
                report_string = st.session_state.compliance_report
                is_pass = report_string.startswith("SCORE: PASS") or "SCORE: PASS" in report_string.split('\n')[0]
                
                if is_pass:
                    st.success("🎉 BRAND GUARDIAN GATEKEEPER: POSITIONING MATRIX CLEARED (PASSED)")
                    st.info(report_string)
                else:
                    st.error("🚨 BRAND GUARDIAN GATEKEEPER: COMPLIANCE INTEGRITY THREAT DETECTED (FAILED)")
                    st.warning("### 📋 Required Instructional Copy Revisions")
                    
                    # Strips out any stray meta-tags the model attempts to generate
                    clean_report = report_string.replace("SCORE: FAIL", "").strip()
                    st.markdown(clean_report)

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
                        with st.spinner("Pushing metrics..."):
                            payload["status"] = "draft"
                            if st.session_state.get("active_item_id"):
                                supabase.table("brand_content_items").update(payload).eq("id", st.session_state.active_item_id).execute()
                            else:
                                exist_check = supabase.table("brand_content_items").select("id").eq("user_id", user_id).eq("title", content_title).eq("platform", chosen_channel).eq("publish_date", str(publish_date)).execute()
                                if exist_check.data:
                                    st.session_state.active_item_id = exist_check.data[0]["id"]
                                    supabase.table("brand_content_items").update(payload).eq("id", exist_check.data[0]["id"]).execute()
                                else:
                                    res = supabase.table("brand_content_items").insert(payload).execute()
                                    if res.data: st.session_state.active_item_id = res.data[0]["id"]
                            st.success("Draft saved!")
                            time.sleep(1)
                            st.rerun()
                with p_buttons[1]:
                    if st.button("🚀 Approve & Lock for Publication Rollout", use_container_width=True, type="primary", disabled=not is_pass):
                        with st.spinner("Locking validated asset..."):
                            payload["status"] = "approved_for_publishing"
                            if st.session_state.get("active_item_id"):
                                supabase.table("brand_content_items").update(payload).eq("id", st.session_state.active_item_id).execute()
                            else:
                                exist_check = supabase.table("brand_content_items").select("id").eq("user_id", user_id).eq("title", content_title).eq("platform", chosen_channel).eq("publish_date", str(publish_date)).execute()
                                if exist_check.data:
                                    supabase.table("brand_content_items").update(payload).eq("id", exist_check.data[0]["id"]).execute()
                                else:
                                    supabase.table("brand_content_items").insert(payload).execute()
                            
                            st.session_state.active_item_id = None
                            st.session_state.active_content_suggestion = ""
                            st.session_state.workspace_text = ""
                            st.session_state.guardian_rev += 1
                            st.session_state.compliance_report = None
                            st.session_state.content_ready_for_scan = False
                            
                            st.success("Asset pushed to timeline!")
                            time.sleep(1)
                            st.rerun()        

    # =====================================================================
    # SIDEBAR ENGINE
    # =====================================================================
    with col_sidebar:
        st.markdown("### 📅 Active Production Timelines")
        calendar_data = load_content_calendar(user_id)
        
        # SCHEDULED ITEMS
        st.markdown("#### 🚀 Scheduled for Release")
        approved_items = [i for i in calendar_data if i['status'] == 'approved_for_publishing']
        if not approved_items:
            st.caption("No assets currently locked for deployment loops.")
            
        for item in approved_items:
            with st.container(border=True):
                st.markdown(f"**🟢 {item['title']}**")
                st.caption(f"📅 **Rollout:** {item['publish_date']} | 📱 **Platform:** {item['platform']}")
                
                if st.button("🔍 Review Confirmed Copy", key=f"rev_{item['id']}", use_container_width=True):
                    show_review_modal(item['title'], item['current_body'])
                
                st.write(" ")
                m1, m2 = st.columns(2)
                with m1:
                    if st.button("↩️ Re-Edit", key=f"revert_{item['id']}", use_container_width=True):
                        supabase.table("brand_content_items").update({"status": "draft"}).eq("id", item['id']).execute()
                        st.session_state.active_item_id = item['id']
                        st.session_state.active_title = item['title']
                        st.session_state.active_category = item['category']
                        st.session_state.active_platform = item['platform']
                        try: st.session_state.active_date = datetime.datetime.strptime(item['publish_date'], "%Y-%m-%d").date()
                        except: pass
                        st.session_state.workspace_text = item['current_body']
                        st.session_state.guardian_rev += 1
                        st.rerun()
                with m2:
                    if st.button("🗑️ Delete", key=f"del_pub_{item['id']}", use_container_width=True):
                        supabase.table("brand_content_items").delete().eq("id", item['id']).execute()
                        st.rerun()

        # WORKSPACE DRAFTS RENDERER
        st.write("---")
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
                    if st.button("📂 Load & Edit", key=f"load_draft_{item['id']}", use_container_width=True):
                        st.session_state.campaign_committed = True
                        st.session_state.active_item_id = item['id']
                        st.session_state.active_title = item['title']
                        st.session_state.active_category = item['category']
                        st.session_state.active_platform = item['platform']
                        try: st.session_state.active_date = datetime.datetime.strptime(item['publish_date'], "%Y-%m-%d").date()
                        except: pass
                        st.session_state.workspace_text = item['current_body']
                        st.session_state.guardian_rev += 1
                        st.session_state.active_content_suggestion = item['suggested_body'] or ""
                        st.session_state.compliance_report = item.get('guardian_notes', None)
                        st.session_state.content_ready_for_scan = True if st.session_state.compliance_report else False
                        st.rerun()
                with d_actions[1]:
                    if st.button("🗑️ Delete", key=f"del_draft_{item['id']}", use_container_width=True):
                        supabase.table("brand_content_items").delete().eq("id", item['id']).execute()
                        st.rerun()