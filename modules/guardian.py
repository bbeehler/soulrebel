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
    except: 
        return []

def load_content_calendar(user_id):
    """Fetches planned, drafted, and fully committed assets from database layers."""
    try:
        response = supabase.table("brand_content_items").select("*").eq("user_id", user_id).neq("title", "MASTER_CAMPAIGN_WORKSPACE").order("publish_date").execute()
        return response.data if response.data else []
    except: 
        return []

def clean_display_text(text):
    """Removes backend payload blocks and scrubs any forbidden agency terms."""
    if not text: 
        return ""
    text = re.sub(r"\bGodzspeed\b", "", text, flags=re.IGNORECASE)
    return text.strip()

def invalidate_previous_compliance_scan():
    """Wipes previous audit reports instantly when user text changes are detected."""
    st.session_state.compliance_report = None
    st.session_state.content_ready_for_scan = False

@st.dialog("📋 Review Confirmed Asset Copy", width="large")
def show_review_modal(item_title, item_body):
    """Renders a clean, centered overlay window to safely inspect published copy scripts."""
    st.markdown(f"### {item_title}")
    st.code(item_body, language="text")
    if st.button("Close"): 
        st.rerun()

def run(user_id):
    st.title("🛡️ The Brand Campaign & Guardian Control")
    st.write("---")

    # --- STATE MANAGEMENT ---
    if "guardian_rev" not in st.session_state: st.session_state.guardian_rev = 0
    if "workspace_text" not in st.session_state: st.session_state.workspace_text = ""
    if "content_ready_for_scan" not in st.session_state: st.session_state.content_ready_for_scan = False
    if "active_item_id" not in st.session_state: st.session_state.active_item_id = None

    # --- METADATA TRACKERS & UI STATE HYDRATION SYNC ---
    if "active_title" not in st.session_state: st.session_state.active_title = ""
    if "active_cat" not in st.session_state: st.session_state.active_cat = None
    if "active_plat" not in st.session_state: st.session_state.active_plat = None

    blueprints = load_blueprints()
    col_main, col_sidebar = st.columns([5, 2], gap="large")

    with col_main:
        # =====================================================================
        # STAGE 01: STRATEGIC DIRECTION
        # =====================================================================
        st.markdown("## 🎯 Stage 1: Strategic Direction")
        st.caption("Strategic parameters successfully integrated from the Master Brand Architecture.")
        
        # =====================================================================
        # STAGE 02: CONTENT GENERATION & BLUEPRINT TAILORING
        # =====================================================================
        st.markdown("## 📝 Stage 2: Content Generation")
        
        # --- UI HYDRATION MATRIX ---
        cats = list(set([b['category'] for b in blueprints]))
        cat_idx = cats.index(st.session_state.active_cat) if st.session_state.active_cat in cats else 0
        
        # Dynamic layout selections connected directly to state loops
        pillar = st.selectbox("Category:", cats, index=cat_idx, key="sel_cat")
        st.session_state.active_cat = pillar
        
        plats = [b['platform'] for b in blueprints if b['category'] == pillar]
        plat_idx = plats.index(st.session_state.active_plat) if st.session_state.active_plat in plats else 0
        channel = st.selectbox("Platform:", plats, index=plat_idx, key="sel_plat")
        st.session_state.active_plat = channel

        title = st.text_input("Asset Title:", value=st.session_state.active_title, key="txt_title")
        st.session_state.active_title = title
        
        instr = st.text_area("Copywriting Instructions:", key="txt_instr")

        # Fetch active blueprint for the prompt payload rules
        blueprint = next((bp for bp in blueprints if bp['category'] == pillar and bp['platform'] == channel), {})

        if st.button("✨ Draft Copy"):
            if not title:
                st.error("Please supply an asset title before running generation parameters.")
            else:
                with st.spinner("Generating..."):
                    # SANDWICH METHOD: Instructions placed first to prevent framework/strategy drift
                    prompt = f"""
                    You are an elite ghostwriter. Write the raw, ready-to-publish copy for: '{title}'.
                    
                    YOUR PRIMARY INSTRUCTIONS: {instr if instr else "Write a compelling post for this platform."}
                    
                    CHANNEL RULES: {channel} | Max Limit Constraints: {PLATFORM_LIMITS.get(channel, {}).get('char_max', 3000)} chars.
                    TONE/STYLE: {blueprint.get('tonal_guardrails', 'Authoritative and clean')}
                    STRUCTURAL RULE: {blueprint.get('structural_rules', 'Direct presentation')}
                    
                    CONTEXT (Background info only - DO NOT mimic this structure):
                    {st.session_state.get('committed_campaign_data', {}).get('architecture', 'N/A')}
                    
                    STRICT RULES:
                    1. Output ONLY the copy text. NO headers, NO strategies, NO advice. Start immediately with copy.
                    2. If Email: Start with Subject line, then the body layout text blocks.
                    3. DO NOT use 'Godzspeed'.
                    """
                    raw = get_soul_rebel_consultant("Copywriter", prompt)
                    st.session_state.workspace_text = clean_display_text(raw)
                    st.session_state.guardian_rev += 1
                    st.rerun()

        # Canvas with active text invalidation hooks on modification loop triggers
        canvas = st.text_area(
            "Canvas:", 
            value=st.session_state.workspace_text, 
            height=300, 
            key=f"c_{st.session_state.guardian_rev}",
            on_change=invalidate_previous_compliance_scan
        )
        st.session_state.workspace_text = canvas
        
        if st.button("🔒 Lock & Scan"):
            if not st.session_state.workspace_text:
                st.error("Canvas is empty. Add copy text before locking workspace parameters.")
            else:
                st.session_state.content_ready_for_scan = True
                st.rerun()

        # =====================================================================
        # STAGE 03: HARD COMPLIANCE AUDIT GATE
        # =====================================================================
        if st.session_state.content_ready_for_scan:
            st.markdown("---")
            if st.button("🔍 Run Audit", type="primary"):
                with st.spinner("Running brand compliance scan..."):
                    audit_prompt = f"""
                    Audit this copy text for brand alignment. 
                    Line 1 MUST read exactly 'SCORE: PASS' or 'SCORE: FAIL'. 
                    If it fails, list 3 actionable bulleted 'Required Fixes' detailing exactly what needs revision.
                    
                    TEXT TO SCAN:
                    {st.session_state.workspace_text}
                    """
                    res = get_soul_rebel_consultant("Auditor", audit_prompt)
                    st.session_state.compliance_report = res
                    st.rerun()

            if st.session_state.get("compliance_report"):
                res_report = st.session_state.compliance_report
                if "SCORE: PASS" in res_report:
                    st.success("🎉 BRAND GUARDIAN GATEKEEPER: POSITIONING MATRIX CLEARED (PASSED)")
                    st.info(res_report)
                    
                    if st.button("🚀 Save/Commit to Production Timeline", use_container_width=True):
                        payload = {
                            "user_id": user_id, 
                            "title": st.session_state.active_title, 
                            "current_body": st.session_state.workspace_text, 
                            "category": st.session_state.active_cat, 
                            "platform": st.session_state.active_plat, 
                            "status": "approved_for_publishing",
                            "publish_date": str(datetime.date.today())
                        }
                        if st.session_state.active_item_id:
                            supabase.table("brand_content_items").update(payload).eq("id", st.session_state.active_item_id).execute()
                        else:
                            supabase.table("brand_content_items").insert(payload).execute()
                        
                        st.success("Asset pushed to timeline production loops!")
                        time.sleep(0.5)
                        st.session_state.active_item_id = None
                        st.session_state.workspace_text = ""
                        st.session_state.active_title = ""
                        st.session_state.compliance_report = None
                        st.session_state.content_ready_for_scan = False
                        st.session_state.guardian_rev += 1
                        st.rerun()
                else:
                    st.error("🚨 BRAND GUARDIAN GATEKEEPER: COMPLIANCE INTEGRITY THREAT DETECTED (FAILED)")
                    st.info(res_report)
            
            if st.button("🔓 Unlock to Edit"):
                st.session_state.content_ready_for_scan = False
                st.rerun()

    with col_sidebar:
        # =====================================================================
        # SIDEBAR ASSET WORKFLOW CONTROLLER
        # =====================================================================
        st.markdown("### 📅 Active Production Timelines")
        calendar_items = load_content_calendar(user_id)
        
        if not calendar_items:
            st.caption("Timeline is currently empty.")
        else:
            for item in calendar_items:
                status_color = "🟢" if item.get("status") == "approved_for_publishing" else "🗂️"
                with St.container(border=True):
                    st.markdown(f"**{status_color} {item['title']}**")
                    st.caption(f"Platform: `{item['platform']}`")
                    
                    col_b1, col_b2 = st.columns(2)
                    with col_b1:
                        if st.button("🔍 View", key=f"v_{item['id']}", use_container_width=True):
                            show_review_modal(item['title'], item['current_body'])
                    with col_b2:
                        # FIXED: Keys completely aligned back to Stage 2 inputs to execute immediate hydration updates
                        if st.button("📂 Load", key=f"l_{item['id']}", use_container_width=True):
                            st.session_state.active_item_id = item['id']
                            st.session_state.workspace_text = item['current_body']
                            st.session_state.active_title = item['title']
                            st.session_state.active_cat = item['category']
                            st.session_state.active_plat = item['platform']
                            st.session_state.compliance_report = None
                            st.session_state.content_ready_for_scan = False
                            st.session_state.guardian_rev += 1
                            st.rerun()