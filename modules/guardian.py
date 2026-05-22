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
    "Facebook": {"char_max": 5000},
    "Instagram": {"char_max": 2200},
    "LinkedIn": {"char_max": 3000},
    "TikTok": {"char_max": 2200},
    "Website Blog": {"char_max": 99999},
    "Substack Blog": {"char_max": 99999}
}

def load_blueprints():
    try:
        response = supabase.table("brand_content_blueprints").select("*").execute()
        return response.data if response.data else []
    except: return []

def load_content_calendar(user_id):
    try:
        response = supabase.table("brand_content_items").select("*").eq("user_id", user_id).neq("title", "MASTER_CAMPAIGN_WORKSPACE").order("publish_date").execute()
        return response.data if response.data else []
    except: return []

def clean_display_text(text):
    if not text: return ""
    text = re.sub(r"\bGodzspeed\b", "", text, flags=re.IGNORECASE)
    return text.strip()

@st.dialog("📋 Review Confirmed Asset Copy", width="large")
def show_review_modal(item_title, item_body):
    st.markdown(f"### {item_title}")
    st.code(item_body, language="text")
    if st.button("Close"): st.rerun()

def run(user_id):
    st.title("🛡️ Brand Guardian")

    # State Management
    if "campaign_committed" not in st.session_state: st.session_state.campaign_committed = False
    if "workspace_text" not in st.session_state: st.session_state.workspace_text = ""
    if "guardian_rev" not in st.session_state: st.session_state.guardian_rev = 0
    if "content_ready_for_scan" not in st.session_state: st.session_state.content_ready_for_scan = False

    # Metadata Trackers
    if "active_item_id" not in st.session_state: st.session_state.active_item_id = None

    col_main, col_sidebar = st.columns([5, 2])

    with col_main:
        # STRATEGY STAGE
        st.markdown("## 🎯 Stage 1: Strategic Direction")
        # [Strategy logic remains the same as your functional version]
        
        # CONTENT STAGE
        st.markdown("## 📝 Stage 2: Content Generation")
        blueprints = load_blueprints()
        cats = list(set([bp['category'] for bp in blueprints]))
        
        # Bind keys to force updates when loading drafts
        pillar = st.selectbox("Category:", cats, key="ui_cat", disabled=st.session_state.content_ready_for_scan)
        channels = [bp['platform'] for bp in blueprints if bp['category'] == pillar]
        channel = st.selectbox("Platform:", channels, key="ui_chan", disabled=st.session_state.content_ready_for_scan)
        title = st.text_input("Title:", key="ui_title", disabled=st.session_state.content_ready_for_scan)
        prompt_instr = st.text_area("Copywriting Instructions:", key="ui_instr", disabled=st.session_state.content_ready_for_scan)

        blueprint = next((bp for bp in blueprints if bp['category'] == pillar and bp['platform'] == channel), {})

        if st.button("✨ Draft Copy"):
            with st.spinner("Generating..."):
                # SANDWICH METHOD: Instructions first to prevent drift
                prompt = f"""
                You are an elite ghostwriter. Write the raw, ready-to-publish copy for: '{title}'.
                
                YOUR PRIMARY INSTRUCTIONS: {prompt_instr if prompt_instr else "Write a compelling post for this platform."}
                
                CHANNEL RULES: {channel} | Max: {PLATFORM_LIMITS.get(channel, {}).get('char_max', 3000)} chars.
                TONE/STYLE: {blueprint.get('tonal_guardrails', 'Authoritative')}
                
                CONTEXT (Background info only - DO NOT mimic this structure):
                {st.session_state.get('committed_campaign_data', {}).get('architecture', 'N/A')}
                
                STRICT RULES:
                1. Output ONLY the copy text. NO headers, NO strategies, NO advice.
                2. If Email: Start with Subject line, then body.
                3. DO NOT use 'Godzspeed'.
                """
                raw = get_soul_rebel_consultant("Copywriter", prompt)
                st.session_state.workspace_text = clean_display_text(raw)
                st.rerun()

        # Canvas
        canvas = st.text_area("Canvas:", value=st.session_state.workspace_text, height=300, key=f"c_{st.session_state.guardian_rev}")
        
        if st.button("🔒 Lock & Scan"):
            st.session_state.workspace_text = canvas
            st.session_state.content_ready_for_scan = True
            st.rerun()

        # AUDIT
        if st.session_state.content_ready_for_scan:
            if st.button("🔍 Run Audit"):
                audit_prompt = f"Audit this copy. Line 1: 'SCORE: PASS' or 'SCORE: FAIL'. If fail, list 3 actionable bulleted 'Required Fixes'.\n{st.session_state.workspace_text}"
                res = get_soul_rebel_consultant("Auditor", audit_prompt)
                st.info(res)
                
                if "SCORE: PASS" in res:
                    if st.button("💾 Save/Commit"):
                        payload = {"user_id": user_id, "title": title, "current_body": st.session_state.workspace_text, "category": pillar, "platform": channel, "status": "approved_for_publishing"}
                        if st.session_state.active_item_id:
                            supabase.table("brand_content_items").update(payload).eq("id", st.session_state.active_item_id).execute()
                        else:
                            supabase.table("brand_content_items").insert(payload).execute()
                        st.success("Committed!")
                        st.rerun()
            
            if st.button("🔓 Unlock to Edit"):
                st.session_state.content_ready_for_scan = False
                st.rerun()

    with col_sidebar:
        st.markdown("### 📝 Vault")
        for item in load_content_calendar(user_id):
            with st.container(border=True):
                st.write(f"**{item['title']}**")
                if st.button("📂 Load", key=f"l_{item['id']}"):
                    st.session_state.active_item_id = item['id']
                    st.session_state.workspace_text = item['current_body']
                    # Force update the widget keys
                    st.session_state.ui_title = item['title']
                    st.session_state.ui_cat = item['category']
                    st.session_state.ui_chan = item['platform']
                    st.session_state.guardian_rev += 1
                    st.rerun()