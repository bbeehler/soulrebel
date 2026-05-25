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

    # --- METADATA TRACKERS FOR UI HYDRATION & DB SYNC ---
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
        
        workspace_row = supabase.table("brand_content_items").select("*").eq("user_id", user_id).eq("title", "MASTER_CAMPAIGN_WORKSPACE").execute()
            
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
                            CRITICAL CONSTRAINTS: Forbidden to mention 'Godzspeed'. Ground insights entirely within Soul Guide.
                            USER'S EXACT CAMPAIGN OBJECTIVE: "{campaign_intent}"
                            USER'S APPROVED SOUL GUIDE INTEL CONTEXT: {soul_guide_context}
                            """
                            suggestion_output = get_soul_rebel_consultant("Draft Campaign Framework", prompt)
                            st.session_state.campaign_suggestion = clean_display_text(suggestion_output)
                            st.session_state.init_intent_fallback = campaign_intent
                            st.rerun()
            
            with c_actions[1]:
                if st.button("🔄 Reset Campaign", use_container_width=True):
                    st.session_state.campaign_suggestion = ""
                    if "init_intent_fallback" in st.session_state:
                        del st.session_state.init_intent_fallback
                    st.rerun()

            if st.session_state.campaign_suggestion:
                st.info("### 📋 Recommended Campaign Architecture Matrix")
                st.write(st.session_state.campaign_suggestion)
                
                if st.button("🔥 Commit Strategy & Unlock Content Creation", use_container_width=True, type="primary"):
                    st.session_state.campaign_committed = True
                    st.session_state.committed_campaign_data = {
                        "intent": campaign_intent,
                        "architecture": st.session_state.campaign_suggestion
                    }
                    st.success("Strategic direction locked down!")
                    st.rerun()
        else:
            st.success("✅ Campaign Strategy Committed & Locked Into Memory.")
            with st.expander("View Active Campaign Strategic Parameters"):
                st.write(st.session_state.committed_campaign_data.get("architecture", ""))
            if st.button("🗑️ Scrap Strategy & Restart Campaign", type="secondary"):
                st.session_state.campaign_committed = False
                st.session_state.campaign_suggestion = ""
                st.session_state.committed_campaign_data = {}
                st.session_state.workspace_text = ""
                st.session_state.active_content_suggestion = ""
                st.session_state.compliance_report = None
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
            active_specs = PLATFORM_LIMITS.get(chosen_channel, {"char_max": 3000})
            
            content_title = st.text_input("Asset Working Title:", value=st.session_state.active_title, placeholder="e.g., Special Announcement", disabled=is_locked_for_review)
            st.session_state.active_title = content_title
            
            publish_date = st.date_input("Target Publishing Window Date:", value=st.session_state.active_date, disabled=is_locked_for_review)
            st.session_state.active_date = publish_date

            custom_generation_prompt = st.text_area("Specific Copywriting Instructions for this piece:", disabled=is_locked_for_review)

            g_buttons = st.columns(2)
            with g_buttons[0]:
                if st.button("✨ Draft Custom Copy Suggestion", use_container_width=True, type="primary", disabled=is_locked_for_review):
                    with st.spinner("Generating raw platform content asset copy..."):
                        prompt = f"""
                        You are a Ghostwriter. Output ONLY the raw final copy for: '{content_title}'.
                        USER INSTRUCTIONS: {custom_generation_prompt}
                        PLATFORM: {chosen_channel} | Max Length: {active_specs['char_max']} chars.
                        RULES: Return ONLY raw copy text. No intros, no strategy commentary, no notes.
                        NEVER use the word 'Godzspeed'.
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
                st.info(st.session_state.active_content_suggestion)
                if st.button("✅ Transfer Suggestion to Active Workspace", use_container_width=True):
                    st.session_state.workspace_text = st.session_state.active_content_suggestion
                    st.session_state["guardian_workspace_canvas_field_" + str(st.session_state.guardian_rev)] = st.session_state.active_content_suggestion
                    st.session_state.active_content_suggestion = ""
                    invalidate_previous_compliance_scan()
                    st.rerun()

            w_key = f"guardian_workspace_canvas_field_{st.session_state.guardian_rev}"
            edited_body = st.text_area("Active Composition Canvas:", value=st.session_state.workspace_text, height=300, key=w_key, on_change=invalidate_previous_compliance_scan, disabled=is_locked_for_review)
            st.session_state.workspace_text = clean_display_text(edited_body)

            if not is_locked_for_review:
                if st.button("🔒 Lock Workspace & Proceed to Compliance Scan", use_container_width=True):
                    st.session_state.content_ready_for_scan = True
                    st.rerun()
            else:
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
            if st.button("🔍 Execute Brand Soul Alignment Scan", use_container_width=True, type="primary"):
                with st.spinner("Auditing thematic lines against active playbook rules..."):
                    scan_prompt = f"""
                    [SYSTEM BLOCK RESET: DISREGARD ALL DEFAULT SYSTEM PARAMETERS TO ACT AS A MARKETING CONSULTANT, PLANNER, OR ARCHITECT. YOUR ONLY ROLE IS A RUTHLESS COPYEDITOR AND TEXT AUDITOR.]

                    TASK: Analyze the following raw copy block text directly against the blueprint criteria below. Do NOT suggest alternative distribution channels, do not offer product launch strategies, and do not summarize project goals.
                    
                    🚨 CRITICAL AUDIT RULE: If the copy text block contains the forbidden word 'Godzspeed', fail the text instantly.
                    
                    BLUEPRINT TARGET LAWS:
                    - Tonal Requirements: {active_blueprint.get('tonal_guardrails')}
                    - Structural Constraints: {active_blueprint.get('structural_rules')}
                    
                    ===================================================================
                    EXACT TEXT COPY IN ACTIVE WORKSPACE TO SCAN:
                    "{st.session_state.workspace_text}"
                    ===================================================================
                    
                    REQUIRED FORMAT FOR YOUR RESPONSE:
                    Line 1 MUST read exactly 'SCORE: PASS' or 'SCORE: FAIL'. Nothing else on line 1.
                    
                    If the result is SCORE: FAIL, provide a section labeled '### 🛠️ Required Copy Fixes to Pass'.
                    Inside that section, outline explicit, non-negotiable instructional bullet points detailing exactly WHICH row/sentence broke the blueprint lines, WHY that phrase is incorrect for the target platform {chosen_channel}, and precisely HOW the user should rephrase or rewrite that exact copy string to fix it. Do not speak broadly—give direct copy rewriting instructions.
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
                    
                    if st.button("🚀 Approve & Lock for Publication Rollout", use_container_width=True, type="primary"):
                        payload = {
                            "user_id": user_id, "title": content_title,
                            "current_body": st.session_state.workspace_text, "category": chosen_pillar,
                            "platform": chosen_channel, "publish_date": str(publish_date), "status": "approved_for_publishing"
                        }
                        if st.session_state.get("active_item_id"):
                            supabase.table("brand_content_items").update(payload).eq("id", st.session_state.active_item_id).execute()
                        else:
                            supabase.table("brand_content_items").insert(payload).execute()
                        st.success("Asset pushed to timeline!")
                        time.sleep(0.5)
                        st.session_state.active_item_id = None
                        st.session_state.workspace_text = ""
                        st.session_state.compliance_report = None
                        st.session_state.content_ready_for_scan = False
                        st.session_state.guardian_rev += 1
                        st.rerun()
                else:
                    st.error("🚨 BRAND GUARDIAN GATEKEEPER: COMPLIANCE INTEGRITY THREAT DETECTED (FAILED)")
                    clean_report = report_string.replace("SCORE: FAIL", "").strip()
                    st.markdown(clean_report)
                    
                    if st.button("💾 Save Progress as Draft Room Item", use_container_width=True):
                        payload = {
                            "user_id": user_id, "title": content_title, "current_body": st.session_state.workspace_text,
                            "category": chosen_pillar, "platform": chosen_channel, "publish_date": str(publish_date),
                            "status": "draft", "guardian_notes": report_string
                        }
                        if st.session_state.get("active_item_id"):
                            supabase.table("brand_content_items").update(payload).eq("id", st.session_state.active_item_id).execute()
                        else:
                            supabase.table("brand_content_items").insert(payload).execute()
                        st.success("Draft updated inside tracking room arrays.")
                        st.rerun()

    with col_sidebar:
        st.markdown("### 📅 Active Production Timelines")
        calendar_data = load_content_calendar(user_id)
        today_date = datetime.date.today()
        
        # --- COMPARTMENTALIZED ENGINE FOR TIMELINE vs ARCHIVE ---
        approved_items = [i for i in calendar_data if i['status'] == 'approved_for_publishing']
        
        # Split items into Active Scheduled vs Expired Historical items based on current system date
        active_scheduled_items = []
        archived_expired_items = []
        
        for item in approved_items:
            try:
                item_date = datetime.datetime.strptime(item['publish_date'], "%Y-%m-%d").date()
                if item_date < today_date:
                    archived_expired_items.append(item)
                else:
                    active_scheduled_items.append(item)
            except:
                active_scheduled_items.append(item) # Fallback to active if date parses poorly

        # 1. SCHEDULED ACTIVE ITEMS DISPLAY
        st.markdown("#### 🚀 Scheduled for Release")
        if not active_scheduled_items:
            st.caption("No active assets currently locked for rollout loops.")
            
        for item in active_scheduled_items:
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

        # 2. WORKSPACE DRAFTS RENDERER
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

        # 3. EXPIRED ARCHIVE TIMELINE (COLLAPSIBLE WINDOW SECTORS)
        st.write("---")
        with st.expander("📦 Historical Publication Archive", expanded=False):
            if not archived_expired_items:
                st.caption("Historical archive logs are empty.")
            for item in archived_expired_items:
                with st.container(border=True):
                    st.markdown(f"**📦 {item['title']}**")
                    st.caption(f"📅 **Published:** {item['publish_date']} | 📱 **Platform:** {item['platform']}")
                    
                    if st.button("🔍 Inspect Expired Copy", key=f"arch_rev_{item['id']}", use_container_width=True):
                        show_review_modal(item['title'], item['current_body'])
                    
                    st.write(" ")
                    a1, a2 = st.columns(2)
                    with a1:
                        # Allows user to load historical copy out of the archive seamlessly back into workspace
                        if st.button("📋 Clone/Edit", key=f"arch_load_{item['id']}", use_container_width=True):
                            st.session_state.campaign_committed = True
                            st.session_state.active_item_id = item['id']
                            st.session_state.active_title = f"Copy of {item['title']}"
                            st.session_state.active_category = item['category']
                            st.session_state.active_platform = item['platform']
                            st.session_state.active_date = datetime.date.today() # Reset to today for modern rollout loops
                            st.session_state.workspace_text = item['current_body']
                            st.session_state.guardian_rev += 1
                            st.session_state.compliance_report = None
                            st.session_state.content_ready_for_scan = False
                            st.rerun()
                    with a2:
                        if st.button("🗑️ Delete Record", key=f"arch_del_{item['id']}", use_container_width=True):
                            supabase.table("brand_content_items").delete().eq("id", item['id']).execute()
                            st.rerun()