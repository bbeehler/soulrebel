import streamlit as st
import datetime
import time
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

def parse_strategy_elements(architecture_text):
    """
    Surgically extracts custom campaign pillars and recommended platforms 
    directly from the Stage 1 generated strategy text block.
    """
    pillars = []
    channels = []
    
    if not architecture_text:
        return ["General Campaign Execution"], list(PLATFORM_LIMITS.keys())
        
    # Extract pillars via common markdown patterns or bullet lines under headers
    pillar_block = re.findall(r"(?:Pillars|PILLARS).*?\n(.*?)(?:\n\n|\n#|$)", architecture_text, re.DOTALL | re.IGNORECASE)
    if pillar_block:
        lines = pillar_block[0].split("\n")
        for line in lines:
            clean = re.sub(r"^[\s\-\*\d\.]+", "", line).strip()
            if clean and len(clean) > 3 and not clean.startswith("#"):
                pillars.append(clean.split(":")[0].strip())
                
    # Fallback if specific bullet parsing yields nothing
    if not pillars:
        pillars = ["Campaign Alignment Core", "Tactical Engagement Narrative", "Distribution Outreach Operational"]

    # Match platform strings explicitly against our system API limit keys
    for plat in PLATFORM_LIMITS.keys():
        if re.search(r"\b" + re.escape(plat) + r"\b", architecture_text, re.IGNORECASE):
            channels.append(plat)
            
    if not channels:
        channels = list(PLATFORM_LIMITS.keys())
        
    return pillars, channels

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
        st.error(f"Error pulling calendar matrix rows: {e}")
        return []

def run(user_id):
    st.title("🛡️ The Brand Campaign & Guardian Control")
    st.caption("From High-Level Campaign Formulation to Hard Omni-Channel Compliance Audits.")
    st.write("---")

    # --- 1. PERSISTENT WORKSPACE STATE ENGINE MANAGEMENT ---
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

    # --- INITIAL LOAD ENGINE: Rehydrate from existing Content Items table row ---
    soul_guide_context = ""
    try:
        strategy_res = supabase.table("brand_strategy").select("soul_guide").eq("user_id", user_id).single().execute()
        soul_guide_context = strategy_res.data.get("soul_guide", "") if strategy_res.data else ""
        
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
                    "intent": record.get("current_body", ""),
                    "architecture": record.get("suggested_body", "")
                }
            elif status_flag == "draft" and not st.session_state.campaign_suggestion:
                st.session_state.campaign_suggestion = record.get("suggested_body", "")
                if "init_intent_fallback" not in st.session_state:
                    st.session_state.init_intent_fallback = record.get("current_body", "")
    except Exception as e:
        pass

    # Layout Split: Central Operational Stepper on left vs Live Timeline on right
    col_main, col_sidebar = st.columns([5, 2], gap="large")

    with col_main:
        # =====================================================================
        # STAGE 01: THE STRATEGIC CAMPAIGN BUILDER
        # =====================================================================
        st.markdown("## 🎯 Stage 1: Campaign Strategic Direction")
        
        if not st.session_state.campaign_committed:
            fallback_text = st.session_state.get("init_intent_fallback", "")
            campaign_intent = st.text_area(
                "Describe your campaign objective or initiative purpose:",
                value=fallback_text,
                placeholder="e.g., We are organizing a charity campaign to raise money for municipal services...",
                help="Type what you want to accomplish. The system will figure out the marketing pillars and optimal distribution mix."
            )
            
            c_actions = st.columns([1, 1, 2])
            with c_actions[0]:
                if st.button("🔮 Brainstorm Strategy", use_container_width=True, type="primary"):
                    if not campaign_intent:
                        st.error("Please provide an initialization objective first.")
                    else:
                        with st.spinner("Formulating channel mix matrix strategies..."):
                            prompt = f"""
                            ROLE: Chief Marketing Officer & Strict Campaign Architect.
                            TASK: Take the user's specific campaign objective and structure it into a clean, execution-ready channel distribution framework.
                            
                            =======================================================================
                            ⚠️ UNYIELDING CORE COMMANDS:
                            - You must ONLY use, frame, and structure the exact core topic, objective, and campaign idea specified by the user below.
                            - You are ABSOLUTELY BANNED from introducing outside concepts, tangent industries, extra creative initiatives, or peripheral sub-topics. 
                            - Do NOT expand, hallucinate, or generalize beyond what the user wrote. Your job is to package their exact idea into strategic channels, not to invent a new one.
                            - Completely omit and never output the word 'Godzspeed'.
                            =======================================================================
                            
                            USER'S EXACT CAMPAIGN OBJECTIVE: 
                            "{campaign_intent}"
                            
                            USER'S STRATEGIC BRAND IDENTITY CONTEXT: 
                            {soul_guide_context}
                            
                            OUTPUT FORMAT: Present the structured framework matching these exact headers:
                            ### 📋 Executive Summary
                            (A concise strategic distillation focusing purely on the execution of the user's exact stated objective)
                            
                            ### 🗂️ Activated Brand Pillars
                            (List exactly 3 or 4 clear, specific campaign pillars activated by this exact project name)
                            
                            ### 📱 Recommended Distribution Channels
                            (List exactly which core platforms from this selection are required: Facebook, Instagram, LinkedIn, TikTok, Website Blog, Substack Blog)
                            """
                            suggestion_output = get_soul_rebel_consultant("Draft Campaign Framework", prompt)
                            
                            sync_payload = {
                                "user_id": user_id,
                                "title": "MASTER_CAMPAIGN_WORKSPACE",
                                "current_body": campaign_intent,
                                "suggested_body": suggestion_output,
                                "status": "draft",
                                "category": "CAMPAIGN_SYSTEM",
                                "platform": "SYSTEM_WORKBENCH",
                                "publish_date": str(datetime.date.today())
                            }
                            try:
                                check_row = supabase.table("brand_content_items").select("id").eq("user_id", user_id).eq("title", "MASTER_CAMPAIGN_WORKSPACE").execute()
                                if check_row.data:
                                    supabase.table("brand_content_items").update(sync_payload).eq("id", check_row.data[0]["id"]).execute()
                                else:
                                    supabase.table("brand_content_items").insert(sync_payload).execute()
                            except:
                                pass

                            st.session_state.campaign_suggestion = suggestion_output
                            st.session_state.init_intent_fallback = campaign_intent
                            st.rerun()
            
            with c_actions[1]:
                if st.button("🔄 Reset Campaign", use_container_width=True):
                    try:
                        supabase.table("brand_content_items").delete().eq("user_id", user_id).eq("title", "MASTER_CAMPAIGN_WORKSPACE").execute()
                    except:
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
                        "user_id": user_id,
                        "title": "MASTER_CAMPAIGN_WORKSPACE",
                        "current_body": campaign_intent,
                        "suggested_body": st.session_state.campaign_suggestion,
                        "status": "approved_for_publishing",
                        "category": "CAMPAIGN_SYSTEM",
                        "platform": "SYSTEM_WORKBENCH",
                        "publish_date": str(datetime.date.today())
                    }
                    try:
                        check_row = supabase.table("brand_content_items").select("id").eq("user_id", user_id).eq("title", "MASTER_CAMPAIGN_WORKSPACE").execute()
                        if check_row.data:
                            supabase.table("brand_content_items").update(commit_payload).eq("id", check_row.data[0]["id"]).execute()
                        else:
                            supabase.table("brand_content_items").insert(commit_payload).execute()
                    except:
                        pass
                        
                    st.session_state.campaign_committed = True
                    st.session_state.committed_campaign_data = {
                        "intent": campaign_intent,
                        "architecture": st.session_state.campaign_suggestion
                    }
                    st.success("Strategic direction locked and saved safely to production table layers!")
                    time.sleep(1.0)
                    st.rerun()
        else:
            st.success("✅ Campaign Strategy Committed & Locked Into Memory.")
            with st.expander("View Active Campaign Strategic Parameters"):
                st.write(st.session_state.committed_campaign_data.get("architecture", ""))
            if st.button("🗑️ Scrap Strategy & Restart Campaign", type="secondary"):
                try:
                    supabase.table("brand_content_items").delete().eq("user_id", user_id).eq("title", "MASTER_CAMPAIGN_WORKSPACE").execute()
                except:
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
        # STAGE 02: DYNAMIC CONTENT ENGINE (DYNAMIC PILLAR & CHANNEL STREAMING)
        # =====================================================================
        st.markdown("## 📝 Stage 2: Content Generation & Blueprint Tailoring")
        
        if not st.session_state.campaign_committed:
            st.caption("🔒 *Commit to a campaign strategy above to unlock the asset generation terminal.*")
        elif not soul_guide_context:
            st.error("🚨 Master Soul Guide context not detected. Please finalize Phase 03: Illumination first.")
        else:
            # FIXED: Dynamically extract options straight from the Stage 1 output text block
            active_arch = st.session_state.committed_campaign_data.get("architecture", "")
            dynamic_pillars, dynamic_channels = parse_strategy_elements(active_arch)
            
            g_col1, g_col2 = st.columns(2)
            with g_col1:
                chosen_pillar = st.selectbox(
                    "Select Preloaded Campaign Pillar:", 
                    dynamic_pillars,
                    help="These pillars are generated straight from your active Stage 1 strategy block above."
                )
            with g_col2:
                chosen_channel = st.selectbox(
                    "Select Recommended Channel Route:", 
                    dynamic_channels,
                    help="This dropdown filters platforms dynamically based on your committed campaign framework."
                )
            
            active_specs = PLATFORM_LIMITS.get(chosen_channel, {"char_max": 3000, "ideal_image": "1080x1080", "aspect_ratio": "1:1"})
            with st.expander("📱 View Active Platform Layout Constraints", expanded=True):
                st.markdown(f"- **Hard Character Limit:** `{active_specs['char_max']:,}` characters")
                st.markdown(f"- **Target Resolution / Layout:** `{active_specs['ideal_image']}` (`{active_specs['aspect_ratio']}` Aspect)")

            content_title = st.text_input("Asset Working Title:", placeholder="e.g., The Impact of Collective Movement")
            publish_date = st.date_input("Target Publishing Window Date:", datetime.date.today())

            st.write(" ")
            
            # --- ASSET GENERATION INTERFACES ---
            g_buttons = st.columns(2)
            with g_buttons[0]:
                if st.button("✨ Draft Custom Copy Suggestion", use_container_width=True, type="primary"):
                    if not content_title:
                        st.error("Provide a working headline title to fuel the engine parameters context.")
                    else:
                        with st.spinner("Synthesizing copy parameters inside blueprint channels..."):
                            prompt = f"""
                            ROLE: Expert Asset Copywriter.
                            TASK: Draft high-engagement copy that strictly bridges the active campaign direction with the specific brand guide pillar rules.
                            
                            =======================================================================
                            ⚠️ UNYIELDING BOUNDARY CONTROLS:
                            - You are ONLY permitted to write about the exact campaign strategy framework and core topic defined below.
                            - Do NOT invent hooks, stories, variables, or angles outside of this explicit text block. 
                            - Your output copy must completely focus on the specific initiative details provided by the user.
                            - Absolutely do NOT include, output, or use the word 'Godzspeed'.
                            =======================================================================
                            
                            LOCKED STRATEGIC CAMPAIGN MATRIX: 
                            {active_arch}
                            
                            USER'S STATED INITIAL INTENT: 
                            "{st.session_state.committed_campaign_data.get('intent')}"
                            
                            =======================================================================
                            🎯 CRITICAL PILLAR-TO-CHANNEL ALIGNMENT LAWS:
                            - ACTIVE CAMPAIGN PILLAR FOCUS: {chosen_pillar}
                            - TARGET DISTRIBUTION CHANNEL: {chosen_channel}
                            - MAXIMUM ALLOCATED VOLUME CEILING: {active_specs['char_max']} characters (Do NOT cross)
                            =======================================================================
                            
                            Braid the structural elements of your campaign intent text to generate an asset tailored specifically for formatting frameworks inside '{chosen_channel}'.
                            
                            MASTER BRAND INTEL PLAYBOOK SOURCE CONTEXT:
                            {soul_guide_context}
                            
                            WORKING TOPIC HEADLINE: {content_title}
                            
                            OUTPUT: Return only the fully written, ready-to-publish raw copy body blocks. Align formatting rules directly to {chosen_channel}. Do not append introduction remarks or conversational text.
                            """
                            st.session_state.active_content_suggestion = get_soul_rebel_consultant("Draft Content Piece", prompt)
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
                    st.session_state.workspace_text = st.session_state.active_content_suggestion
                    st.session_state.active_content_suggestion = ""
                    st.rerun()

            # --- ACTIVE EDITOR WORKSPACE CANVAS ---
            st.write(" ")
            w_key = f"workspace_rev_layer_{st.session_state.guardian_rev}"
            edited_body = st.text_area(
                "Active Composition Canvas:",
                value=st.session_state.workspace_text,
                height=300,
                key=w_key,
                help="Refine your copy body blocks here. Once you are satisfied with your wording, click Lock Workspace to send it to the Guardian compliance gate below."
            )
            st.session_state.workspace_text = edited_body

            c_length = len(edited_body)
            if c_length > active_specs['char_max']:
                st.error(f"⚠️ Platform Overflow: Copy scales to `{c_length}` characters. This breaks the hard `{active_specs['char_max']}` threshold for {chosen_channel}!")
            else:
                st.caption(f"Volume Tracker: `{c_length}` / `{active_specs['char_max']}` maximum characters for {chosen_channel}.")

            if st.session_state.workspace_text:
                chat_feedback = st.chat_input("Ask the controller to rewrite, extend, or trim this text...")
                if chat_feedback:
                    with st.spinner("Recalibrating narrative lines against layout specs..."):
                        refine_prompt = f"""
                        TASK: Revise the copy text based on user directions. Ensure text bounds fit rules for {chosen_channel}.
                        CRITICAL CONSTRAINT: Focus strictly on the core theme. Do not invent outside narrative hooks or use the word 'Godzspeed'.
                        EXISTING BODY LAYOUT:\n{edited_body}
                        """
                        st.session_state.workspace_text = get_soul_rebel_consultant(chat_feedback, refine_prompt)
                        st.session_state.guardian_rev += 1
                        st.rerun()

                if st.button("🔒 Lock Workspace & Proceed to Compliance Scan", use_container_width=True):
                    st.session_state.content_ready_for_scan = True
                    st.success("Workspace locked. Step 3 Compliance Gate is now authorized to run.")
                    st.rerun()

        st.write("---")

        # =====================================================================
        # STAGE 03: HARD COMPLIANCE AUDIT GATE
        # =====================================================================
        st.markdown("## 🛡️ Stage 3: Brand Guardian Compliance Gate")
        
        if not st.session_state.content_ready_for_scan:
            st.caption("🔒 *Complete your workspace composition steps above and lock down composition to clear the compliance pathways.*")
        else:
            st.warning(f"**Target System Rule Check:** Auditing copy against {chosen_channel} rules (Limit: `{active_specs['char_max']}` chars) under the context of the active campaign profile parameters.")
            
            if st.button("🔍 Execute Brand Soul Alignment Scan", use_container_width=True, type="primary"):
                with st.spinner("Auditing thematic lines against active playbook rules..."):
                    scan_prompt = f"""
                    ROLE: Hardened Compliance Auditor & Channel Integrity Sweeper.
                    TASK: Audit this text copy against absolute architectural limits, active pillars, and user campaign directives.
                    
                    CRITICAL COMPLIANCE FILTER: 
                    Verify that this copy matches the user's committed campaign focus topic perfectly. If the copy drifts into unrelated fields, irrelevant stories, or ignores the committed campaign architecture context, you must trigger a hard FAIL.
                    
                    HARD PLATFORM CONSTRAINT MANDATE:
                    If the total character volume of the provided text (`{c_length}`) exceeds the platform limit threshold of `{active_specs['char_max']}`, you MUST immediately issue a hard FAIL.
                    
                    MANDATE: Completely omit the word 'Godzspeed'.
                    
                    LOCKED CAMPAIGN BLUEPRINT ARCHITECTURE:
                    {active_arch}
                    
                    USER'S STATED INITIAL INTENT: 
                    "{st.session_state.committed_campaign_data.get('intent')}"
                    
                    USER CAMPAIGN FOCUS PILLAR: {chosen_pillar}
                    TECHNICAL PLATFORM CONSTRAINTS: {chosen_channel} (Max Chars: {active_specs['char_max']})
                    CORE SYSTEM BRAND GUIDE INTEGRITY CONTEXT: {soul_guide_context}
                    
                    TEXT TO AUDIT:
                    {edited_body}
                    
                    OUTPUT LAYOUT FORMAT RULES: Your return sequence parameters must match this format structure:
                    Line 1 must contain exactly either 'SCORE: PASS' or 'SCORE: FAIL'.
                    Follow with a markdown heading titled '### 📊 Compliance Diagnostic Summary Notes' and outline structural breakdowns explaining the positioning or character-count violation reasons.
                    """
                    st.session_state.compliance_report = get_soul_rebel_consultant("Verify Asset Integrity", scan_prompt)
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
                    "suggested_body": st.session_state.active_content_suggestion, "current_body": edited_body,
                    "category": chosen_pillar, "platform": chosen_channel,
                    "publish_date": str(publish_date), "guardian_notes": report_string
                }

                p_buttons = st.columns(2)
                with p_buttons[0]:
                    if st.button("💾 Save Progress as Draft Room Item", use_container_width=True):
                        with st.spinner("Pushing record metrics to database lines..."):
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
                        with st.spinner("Locking validated assets down to production lines..."):
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
                            st.success("Asset cleared and pushed to live operational schedule timeline!")
                            time.sleep(1)
                            st.rerun()

    # =====================================================================
    # RIGHT SIDEBAR TIMELINE ENGINE: FULL CRUD LAYER VIA ACTION RE-ROUTING
    # =====================================================================
    with col_sidebar:
        st.markdown("### 📅 Active Production Timelines")
        st.caption("Manage, edit, or delete items within your strategy stream.")
        st.write("---")
        
        calendar_data = load_content_calendar(user_id)
        
        if not calendar_data:
            st.info("Your tactical rollout timeline pipeline is currently empty.")
        else:
            st.markdown("#### 🚀 Approved & Scheduled for Release")
            approved_items = [i for i in calendar_data if i['status'] == 'approved_for_publishing']
            if not approved_items:
                st.caption("No assets currently locked for field execution deployment loops.")
            for item in approved_items:
                with st.container(border=True):
                    st.markdown(f"**🟢 {item['title']}**")
                    st.caption(f"📅 **Rollout:** {item['publish_date']} | 📱 **Platform:** {item['platform']}")
                    
                    with st.expander("Review Confirmed Asset Script Copy"):
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
                st.caption("No work-in-progress drafts currently sitting inside repository tracks.")
            for item in draft_items:
                with st.container(border=True):
                    st.markdown(f"**🗂️ {item['title']}**")
                    st.caption(f"📅 **Target Window:** {item['publish_date']} | 🛠️ **Platform:** {item['platform']}")
                    
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