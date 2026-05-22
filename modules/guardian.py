import streamlit as st
import datetime
import time
import json
import re
from utils.gemini_ai import get_soul_rebel_consultant
from utils.supabase_db import supabase

# =====================================================================
# PLATFORM SPECS
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
    # Scrub agency name and any meta-headers the AI might try to sneak in
    text = re.sub(r"\bGodzspeed\b", "", text, flags=re.IGNORECASE)
    return text.strip()

@st.dialog("📋 Review Confirmed Asset Copy", width="large")
def show_review_modal(item_title, item_body):
    st.markdown(f"### {item_title}")
    st.code(item_body, language="text")
    if st.button("Close"): st.rerun()

def run(user_id):
    st.title("🛡️ Brand Guardian")
    
    # Initialize States
    if "campaign_committed" not in st.session_state: st.session_state.campaign_committed = False
    if "workspace_text" not in st.session_state: st.session_state.workspace_text = ""
    if "content_ready_for_scan" not in st.session_state: st.session_state.content_ready_for_scan = False

    col_main, col_sidebar = st.columns([5, 2])

    with col_main:
        # STAGE 2: COPY GENERATION (FORCED CONTENT-ONLY)
        st.markdown("## 📝 Stage 2: Content Generation")
        blueprints = load_blueprints()
        
        cats = list(set([bp['category'] for bp in blueprints]))
        chosen_pillar = st.selectbox("Category:", cats)
        channels = [bp['platform'] for bp in blueprints if bp['category'] == chosen_pillar]
        chosen_channel = st.selectbox("Platform:", channels)
        
        blueprint = next((bp for bp in blueprints if bp['category'] == chosen_pillar and bp['platform'] == chosen_channel), {})
        title = st.text_input("Title:")
        instructions = st.text_area("Specific Instructions (e.g., 'Write a high-urgency email'):")

        if st.button("✨ Draft Copy"):
            with st.spinner("Writing..."):
                prompt = f"""
                You are a professional copywriter. 
                Write the RAW COPY for a {chosen_channel} post/email titled '{title}'.
                
                Goal: {instructions}
                Brand Voice: {blueprint.get('tonal_guardrails', 'Authoritative and clear')}
                
                RULES:
                1. Output ONLY the copy text. 
                2. NO intros, NO outlines, NO headers like 'Subject Line:', NO advice.
                3. If it's an email, start with the subject line then the body.
                4. Do not use the word 'Godzspeed'.
                """
                raw_out = get_soul_rebel_consultant("Content Generator", prompt)
                st.session_state.workspace_text = clean_display_text(raw_out)
                st.session_state.content_ready_for_scan = False
                st.rerun()

        # Canvas
        edited_body = st.text_area("Canvas:", value=st.session_state.workspace_text, height=300, key="canvas")
        
        if st.button("🔒 Lock & Scan"):
            st.session_state.workspace_text = edited_body
            st.session_state.content_ready_for_scan = True
            st.rerun()

        # STAGE 3: SCAN
        if st.session_state.content_ready_for_scan:
            if st.button("🔍 Run Audit"):
                scan_prompt = f"Audit this text for brand alignment. Return 'SCORE: PASS' or 'SCORE: FAIL' followed by a brief note:\n{st.session_state.workspace_text}"
                res = get_soul_rebel_consultant("Auditor", scan_prompt)
                st.info(res)
                if "SCORE: PASS" in res:
                    if st.button("🚀 Commit to Timeline"):
                        payload = {"user_id": user_id, "title": title, "current_body": st.session_state.workspace_text, "status": "approved_for_publishing", "platform": chosen_channel, "publish_date": str(datetime.date.today())}
                        supabase.table("brand_content_items").insert(payload).execute()
                        st.success("Committed!")
                        st.rerun()

    with col_sidebar:
        st.markdown("### 📅 Timelines")
        for item in load_content_calendar(user_id):
            with st.container(border=True):
                st.write(f"**{item['title']}**")
                if st.button("🔍 View", key=f"v_{item['id']}"): show_review_modal(item['title'], item['current_body'])