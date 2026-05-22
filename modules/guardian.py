import streamlit as st
import datetime
import time
import re
from utils.gemini_ai import get_soul_rebel_consultant
from utils.supabase_db import supabase

# Hard platform requirements for continuous validation layers
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
        st.error(f"Error loading blueprints from database: {e}")
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
        st.error(f"Error pulling calendar matrix rows: {e}")
        return []

def clean_display_text(architecture_text):
    """Removes the ugly backend data payload block from showing up in the user display field."""
    if not architecture_text:
        return ""
    return re.sub(r"\[PILLARS_DATA_START\].*?\[PILLARS_DATA_END\]", "", architecture_text, flags=re.DOTALL).strip()

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

    # --- INITIAL LIVE SYSTEM HYDRATION LAYER ---
    blueprints = load_blueprints()
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
                            ROLE: Independent Executive Consultant & Chief Marketing Architect.
                            TASK: Take the user's specific campaign objective and structure it into a clean, execution-ready channel distribution framework.
                            
                            =======================================================================
                            🚨 CRITICAL NEGATIVE CONSTRAINT — FORBIDDEN REFERENCES:
                            - You must write purely, directly, and exclusively from the individual user's personal voice.
                            - You are ABSOLUTELY FORBIDDEN from using, referencing, naming, or mentioning the agency name 'Godzspeed' or any outside marketing agency entity anywhere in your text.
                            - Ground all insights entirely within the provided Master Soul Guide document.
                            =======================================================================
                            
                            USER'S EXACT CAMPAIGN OBJECTIVE: "{campaign_intent}"
                            USER'S APPROVED SOUL GUIDE INTEL CONTEXT: {soul_guide_context}
                            
                            OUTPUT FORMAT: Present the structured framework matching these exact headers:
                            ### 📋 Executive Summary
                            (A concise strategic distillation focusing purely on the execution of the user's exact stated objective)
                            
                            ### 🗂️ Activated Brand Pillars
                            (List exactly 3 or 4 clear, specific campaign pillars activated by this project, written as concise short phrases on individual bullet lines)
                            
                            ### 📱 Recommended Distribution Channels
                            (List exactly which platforms from this selection are required: Facebook, Instagram, LinkedIn, TikTok, Website Blog, Substack Blog)
                            """
                            suggestion_output = get_soul_rebel_consultant("Draft Campaign Framework", prompt)
                            
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
                st.write(clean_display_text(st.session_state.campaign_suggestion))
                
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
                    except:
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
                st.write(clean_display_text(st.session_state.committed_campaign_data.get("architecture", "")))
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
        # STAGE 02: DYNAMIC BLUEPRINT CONTENT ENGINE (REAL BLUEPRINTS RELATION CHECK)
        # =====================================================================
        st.markdown("## 📝 Stage 2: Content Generation & Blueprint Tailoring")
        
        if not st.session_state.campaign_committed:
            st.caption("🔒 *Commit to a campaign strategy above to unlock the asset generation terminal.*")
        elif not blueprints:
            st.error("⚠️ No content blueprints found inside table 'brand_content_blueprints'. Run your database seed configurations first.")
        else:
            # FIXED: Dynamically extract distinct categories strictly present inside brand_content_blueprints
            available_categories = list(set([bp['category'] for bp in blueprints]))
            
            g_col1, g_col2 = st.columns(2)
            with g_col1:
                chosen_pillar = st.selectbox(
                    "Active Brand Blueprint Category:", 
                    available_categories,
                    help="Pillars loaded directly from your brand_content_blueprints database schema."
                )
            
            # FIXED: Cascade channel selections down to ONLY match platforms tied to that specific category row
            filtered_platforms = [bp['platform'] for bp in blueprints if bp['category'] == chosen_pillar]
            
            with g_col2:
                chosen_channel = st.selectbox(
                    "Target Publishing Platform:", 
                    filtered_platforms if filtered_platforms else list(PLATFORM_LIMITS.keys()),
                    help="Platforms filtered dynamically based on your chosen blueprint category constraint row."
                )
            
            # Extract active baseline record metadata
            active_blueprint = next((bp for bp in blueprints if bp['category'] == chosen_pillar and bp['platform'] == chosen_channel), None)
            active_specs = PLATFORM_LIMITS.get(chosen_channel, {"char_max": 3000, "ideal_image": "