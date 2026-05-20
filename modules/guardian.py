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

    # 1. INITIALIZE ENVIRONMENT MATRIX
    blueprints = load_blueprints()
    if not blueprints:
        st.warning("⚠️ No content blueprints configured. Please run your reference database migrations.")
        return

    categories = list(set([bp['category'] for bp in blueprints]))

    # Initialize select drop parameters in state to guarantee cross-widget click persistence
    if "guardian_cat_select" not in st.session_state:
        st.session_state.guardian_cat_select = categories[0]
    
    init_plats = [bp['platform'] for bp in blueprints if bp['category'] == st.session_state.guardian_cat_select]
    if "guardian_plat_select" not in st.session_state:
        st.session_state.guardian_plat_select = init_plats[0] if init_plats else ""
        
    if "guardian_title_input" not in st.session_state:
        st.session_state.guardian_title_input = ""
    if "guardian_date_input" not in st.session_state:
        st.session_state.guardian_date_input = datetime.date.today()

    # 2. THE STRATEGIC CALENDAR PARAMETERS PANEL
    st.subheader("📅 Schedule & Parameter Configurations")
    
    col1, col2 = st.columns(2)
    with col1:
        selected_category = st.selectbox("Select Content Category Pillar:", categories, key="guardian_cat_select")
        available_platforms = [bp['platform'] for bp in blueprints if bp['category'] == selected_category]
        
        if st.session_state.guardian_plat_select not in available_platforms and available_platforms:
            st.session_state.guardian_plat_select = available_platforms[0]
            
        selected_platform = st.selectbox("Target Publishing Platform / Channel:", available_platforms, key="guardian_plat_select")
    
    with col2:
        content_title = st.text_input("Asset Working Title:", placeholder="e.g., The Illusion of Public Inclusion", key="guardian_title_input")
        publish_date = st.date_input("Scheduled Publication Date:", key="guardian_date_input")

    active_blueprint = next((bp for bp in blueprints if bp['category'] == selected_category and bp['platform'] == selected_platform), None)

    if active_blueprint:
        with st.expander("🔍 View Channel Blueprint Guardrails", expanded=False):
            st.markdown(f"**Medium Format:** {active_blueprint['medium_type']}")
            st.markdown(f"**Target Depth/Length:** {active_blueprint['target_length']}")
            st.markdown(f"**Strict Tonal Rules:** *{active_blueprint['tonal_guardrails']}*")
            st.markdown(f"**Strict Structural Mandates:** {active_blueprint['structural_rules']}")

    st.write("---")

    # 3. CONTEXT-SPECIFIC STATE AND SELECTION HANDSHAKE
    if "guardian_suggestion" not in st.session_state:
        st.session_state.guardian_suggestion = ""
    if "workspace_text" not in st.session_state:
        st.session_state.workspace_text = ""
    if "compliance_report" not in st.session_state:
        st.session_state.compliance_report = None
    if "last_loaded_key" not in st.session_state:
        st.session_state.last_loaded_key = ""

    current_asset_key = f"{selected_platform}_{content_title}_{publish_date}"
    
    # Auto-load draft from table row if user shifts focus parameters manually
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
        except Exception as e:
            pass

    # 4. BLUEPRINT COMPLIANT GENERATION
    st.subheader("💡 Content Generation & Optimization")
    
    if st.button("✨ Generate Strategic Suggestion from Playbook", use_container_width=True):
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
                st.session_state[f"text_area_{current_asset_key}"] = st.session_state.guardian_suggestion
                st.success("Copy seamlessly transferred to active workspace!")
                time.sleep(0.5)
                st.rerun()
        with s_col2:
            if st.button("❌ Reject Suggestion", use_container_width=True):
                st.session_state.guardian_suggestion = ""
                st.rerun()

    # 5. SPECIFIC ACTIVE LIVE WORKSPACE
    st.write("---")
    st.subheader(f"📝 Workspace: {selected_platform} Asset")
    st.caption(f"Currently managing workspace data for: **{content_title if content_title else 'Untitled Asset'}** targeted for rollout on **{publish_date}**.")
    
    edited_body = st.text_area(
        "Refine, write, or manually format your asset here:",
        value=st.session_state.workspace_text,
        height=350,
        key=f"text_area_{current_asset_key}"
    )
    st.session_state.workspace_text = edited_body

    # COLLABORATIVE REFINEMENT HUB
    if st.session_state.workspace_text:
        user_feedback = st.chat_input("Ask the Guardian to rewrite, expand, or adjust tone parameters for this workspace...")
        if user_feedback:
            with st.spinner("Recalibrating asset against the corporate blueprint..."):
                refine_prompt = f"""
                ROLE: Godzspeed Soul Rebel Brand Guardian.
                TASK: Revise the EXISTING TEXT based on the USER FEEDBACK. Keep tone strict: {active_blueprint['tonal_guardrails']}.
                EXISTING TEXT:\n{edited_body}
                """
                revised_text = get_soul_rebel_consultant(user_feedback, refine_prompt)
                st.session_state.workspace_text = revised_text
                st.session_state[f"text_area_{current_asset_key}"] = revised_text
                st.rerun()

    # 6. COMPLIANCE SCAN MECHANISM
    st.write("---")
    st.subheader("🛡️ Compliance & Core Soul Audit Scan")
    
    c_col1, c_col2 = st.columns([1, 2])
    with c_col1:
        if st.button("🔍 Run Brand Soul Alignment Scan", use_container_width=True, type="secondary"):
            with st.spinner("Analyzing text for playbook alignment violations..."):
                try:
                    strategy_res = supabase.table("brand_strategy").select("soul_guide").eq("user_id", user_id).single().execute()
                    soul_guide_context = strategy_res.data.get("soul_guide", "") if strategy_res.data else ""
                    
                    scan_prompt = f"""
                    TASK: Audit the copy against the strict brand guidelines.
                    - Tone Guide: {active_blueprint['tonal_guardrails']}
                    - Structural Demands: {active_blueprint['structural_rules']}
                    - Core Soul: {soul_guide_context}
                    
                    TEXT TO AUDIT:
                    {edited_body}
                    
                    OUTPUT FORMAT: Return a structured text score report. 
                    1. Start with exactly 'SCORE: PASS' or 'SCORE: FAIL' based on tonal integrity.
                    2. Follow with bulleted analytical notes explaining why it matches or breaks the brand standard.
                    """
                    report = get_soul_rebel_consultant("Audit text", scan_prompt)
                    st.session_state.compliance_report = report
                    st.rerun()
                except Exception as e:
                    st.error(f"Scan error: {e}")

    with c_col2:
        if st.session_state.compliance_report:
            report_text = st.session_state.compliance_report
            is_pass = "SCORE: PASS" in report_text
            
            if is_pass:
                st.success("🎉 BRAND GUARDIAN AUDIT: PASSED")
            else:
                st.error("🚨 BRAND GUARDIAN AUDIT: FAILED COMPLIANCE")
            st.info(report_text)

    # 7. BULLETPROOF CALENDAR SAVE AND COMMIT CONTROL (UPSERT ENGINE)
    st.write("---")
    b_col1, b_col2 = st.columns(2)
    
    payload = {
        "user_id": user_id,
        "title": content_title,
        "suggested_body": st.session_state.guardian_suggestion,
        "current_body": edited_body,
        "category": selected_category,
        "platform": selected_platform,
        "publish_date": str(publish_date),
        "guardian_notes": st.session_state.compliance_report
    }
    
    with b_col1:
        if st.button("💾 Save Progress as Draft", use_container_width=True):
            if not content_title:
                st.error("Please provide an Asset Working Title before committing to the calendar data layers.")
            else:
                with st.spinner("Locking draft to schedule line..."):
                    payload["status"] = "draft"
                    
                    check_exist = supabase.table("brand_content_items").select("id")\
                        .eq("user_id", user_id).eq("title", content_title).eq("platform", selected_platform).eq("publish_date", str(publish_date)).execute()
                        
                    if check_exist.data:
                        supabase.table("brand_content_items").update(payload).eq("id", check_exist.data[0]["id"]).execute()
                    else:
                        supabase.table("brand_content_items").insert(payload).execute()
                        
                    st.success(f"Asset for {selected_platform} saved successfully as a Draft!")
                    time.sleep(1)
                    st.rerun()

    with b_col2:
        has_passed = st.session_state.compliance_report is not None and "SCORE: PASS" in st.session_state.compliance_report
        
        if st.button("🔥 Approve & Commit to Content Pipeline", use_container_width=True, disabled=not has_passed, type="primary"):
            with st.spinner("Locking verified asset into publication calendar..."):
                payload["status"] = "approved_for_publishing"
                
                check_exist = supabase.table("brand_content_items").select("id")\
                    .eq("user_id", user_id).eq("title", content_title).eq("platform", selected_platform).eq("publish_date", str(publish_date)).execute()
                    
                if check_exist.data:
                    supabase.table("brand_content_items").update(payload).eq("id", check_exist.data[0]["id"]).execute()
                else:
                    supabase.table("brand_content_items").insert(payload).execute()
                    
                st.success("Asset cleared by Guardian and locked into active Content Calendar!")
                
                st.session_state.guardian_suggestion = ""
                st.session_state.workspace_text = ""
                st.session_state.compliance_report = None
                st.session_state.last_loaded_key = ""
                time.sleep(1)
                st.rerun()

    # 8. THE INTERACTIVE STRATEGIC KANBAN CONTENT CALENDAR
    st.write("---")
    st.subheader("📅 Live Strategic Content Pipeline Calendar")
    calendar_data = load_content_calendar(user_id)

    if not calendar_data:
        st.caption("No assets currently scheduled in the pipeline matrix.")
    else:
        lane_draft, lane_review, lane_approved = st.columns(3)
        
        with lane_draft:
            st.markdown("### 📝 Work-in-Progress (Drafts)")
            for item in calendar_data:
                if item['status'] == 'draft':
                    with st.container(border=True):
                        st.markdown(f"**{item['title']}**")
                        st.caption(f"📅 **Publish:** {item['publish_date']}\n\n🛠️ **Channel:** {item['platform']} | 🗂️ {item['category']}")
                        
                        if st.button("Open in Active Workspace", key=f"load_item_{item['id']}", use_container_width=True):
                            st.session_state.guardian_cat_select = item['category']
                            st.session_state.guardian_plat_select = item['platform']
                            st.session_state.guardian_title_input = item['title']
                            st.session_state.guardian_date_input = datetime.datetime.strptime(item['publish_date'], "%Y-%m-%d").date()
                            
                            st.session_state.workspace_text = item['current_body']
                            st.session_state.guardian_suggestion = item['suggested_body'] or ""
                            st.session_state.compliance_report = item['guardian_notes']
                            
                            target_key = f"{item['platform']}_{item['title']}_{item['publish_date']}"
                            st.session_state[f"text_area_{target_key}"] = item['current_body']
                            st.session_state.last_loaded_key = target_key
                            st.rerun()

        with lane_review:
            st.markdown("### 🔍 Under Review / Failed Scan")
            for item in calendar_data:
                if item['status'] == 'guardian_review' or (item['status'] == 'draft' and item['guardian_notes'] and "SCORE: FAIL" in item['guardian_notes']):
                    with st.container(border=True):
                        st.markdown(f"**{item['title']}**")
                        st.caption(f"📅 **Publish:** {item['publish_date']}\n\n🛠️ **Channel:** {item['platform']}")

        with lane_approved:
            st.markdown("### 🚀 Approved & Scheduled")
            for item in calendar_data:
                if item['status'] == 'approved_for_publishing':
                    with st.container(border=True):
                        st.markdown(f"🎉 **{item['title']}**")
                        st.caption(f"📅 **Go-Live Date:** {item['publish_date']}\n\n🛠️ **Channel:** {item['platform']}")
                        with st.expander("View Final Cleared Copy"):
                            st.code(item['current_body'])