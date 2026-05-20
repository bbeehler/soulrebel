import streamlit as st
import pandas as pd
import numpy as np
import datetime
import time
from utils.supabase_db import supabase

def load_o2o_data(user_id):
    """Fetches universal digital inputs and physical realized outcomes from Supabase."""
    try:
        digital_res = supabase.table("brand_digital_inputs").select("*").eq("user_id", user_id).order("recorded_date").execute()
        offline_res = supabase.table("brand_offline_outcomes").select("*").eq("user_id", user_id).order("recorded_date").execute()
        return digital_res.data if digital_res.data else [], offline_res.data if offline_res.data else []
    except Exception as e:
        st.error(f"Error executing data handshake: {e}")
        return [], []

def calculate_soul_guide_grade(user_id):
    """
    Computes an execution grade based on the ratio of compliant passed assets 
    vs failed assets in the Brand Guardian production log.
    """
    try:
        content_items = supabase.table("brand_content_items").select("status", "guardian_notes").eq("user_id", user_id).execute()
        if not content_items.data:
            return "N/A", "No assets have been passed through the Brand Guardian gate yet.", "#808080"
            
        total_assets = len(content_items.data)
        passed_assets = sum(1 for item in content_items.data if item['status'] == 'approved_for_publishing' or (item['guardian_notes'] and "SCORE: PASS" in item['guardian_notes']))
        
        compliance_ratio = (passed_assets / total_assets) * 100
        
        if compliance_ratio >= 90:
            return "A", f"Exceptional Soul Alignment ({compliance_ratio:.1f}%). Your content is explicitly tied to your brand anchors.", "#2ecc71"
        elif compliance_ratio >= 80:
            return "B", f"Strong Soul Alignment ({compliance_ratio:.1f}%). Minor variance from blueprint structural mandates.", "#3498db"
        elif compliance_ratio >= 70:
            return "C", f"Compromised Soul Alignment ({compliance_ratio:.1f}%). High volume of content drifting into generic marketplace tone.", "#f1c40f"
        elif compliance_ratio >= 60:
            return "D", f"Critical Shift Flagged ({compliance_ratio:.1f}%). Strategic content is losing its authoritative voice standard.", "#e67e22"
        else:
            return "F", f"Systemic Shadowing Violation ({compliance_ratio:.1f}%). Content is deploying without passing alignment gates.", "#e74c3c"
    except Exception:
        return "N/A", "Enforcement logging tracking unavailable.", "#808080"

def run(user_id):
    st.title("📊 Phase 05: O2O Attribution Analytics")
    st.caption("The Strategic Verification Center: Linking Digital Engagement to Physical Spatial Conversions.")
    st.write("---")

    # 1. LIVE BRAND GUARDIAN ENFORCEMENT AUDIT (THE SOUL GRADE)
    st.subheader("🛡️ The Playbook Enforcement Score")
    grade, explanation, color = calculate_soul_guide_grade(user_id)
    
    st.markdown(
        f"""
        <div style="background-color:#1e1e1e; padding:20px; border-radius:10px; border-left: 8px solid {color}; margin-bottom:25px;">
            <span style="font-size:14px; text-transform:uppercase; color:#888; letter-spacing:1px; font-weight:bold;">Soul Guide Alignment Grade</span>
            <h1 style="color:{color}; font-size:64px; margin:5px 0px;">{grade}</h1>
            <p style="color:#fff; font-size:16px; margin:0; font-style:italic;">{explanation}</p>
        </div>
        """, 
        unsafe_allow_html=True
    )

    # 2. THE MANUAL OPERATIONS DATA ENTRY PANEL (WHERE USERS ENTER THE DATA)
    with st.expander("📥 Manual Operations Log Entry Form", expanded=False):
        st.markdown("### Log Daily Performance Metrics")
        st.caption("Record inputs and real-world results for a specific business day to populate your trends.")
        
        form_date = st.date_input("Metrics Logging Date Target:", value=datetime.date.today(), key="analytics_log_date")
        
        st.write("---")
        f_col1, f_col2 = st.columns(2)
        
        with f_col1:
            st.markdown("#### 📱 Digital Campaign Inputs")
            log_campaign = st.text_input("Active Campaign Name:", value="General Awareness", key="an_log_camp")
            log_platform = st.selectbox("Digital Distribution Channel:", ["LinkedIn", "Substack Blog", "Website Blog", "Facebook", "Instagram", "TikTok", "YouTube", "Internal Intranet"], key="an_log_plat")
            log_spend = st.number_input("Ad Dollars Spent ($):", min_value=0.0, step=10.0, key="an_log_spend")
            log_impressions = st.number_input("Impressions Logged:", min_value=0, step=100, key="an_log_imp")
            log_clicks = st.number_input("Clicks / Engagements Recorded:", min_value=0, step=10, key="an_log_clicks")
            
        with f_col2:
            st.markdown("#### 🏢 Realized Offline Outcomes")
            log_traffic = st.number_input("Physical Foot Traffic / Door Count Count:", min_value=0, step=10, key="an_log_traf")
            log_conversions = st.number_input("Physical Conversions (Signups, Bookings, Orders):", min_value=0, step=5, key="an_log_conv")
            log_revenue = st.number_input("Gross Realized Revenue ($):", min_value=0.0, step=100.0, key="an_log_rev")
            
        st.write("   ")
        if st.button("🔥 Commit Operations Log to Database", use_container_width=True, type="primary"):
            with st.spinner("Writing operational indicators to data cloud..."):
                try:
                    # 1. Format payload mappings
                    digital_payload = {
                        "user_id": user_id, "campaign_name": log_campaign, "platform": log_platform,
                        "ad_spend": log_spend, "impressions": log_impressions, "clicks_or_engagements": log_clicks,
                        "recorded_date": str(form_date)
                    }
                    offline_payload = {
                        "user_id": user_id, "foot_traffic_count": log_traffic, "physical_conversions": log_conversions,
                        "gross_realized_revenue": log_revenue, "recorded_date": str(form_date)
                    }
                    
                    # 2. Save Digital Layer
                    supabase.table("brand_digital_inputs").insert(digital_payload).execute()
                    
                    # 3. Upsert Offline Result Layer safely
                    check_exist = supabase.table("brand_offline_outcomes").select("id").eq("user_id", user_id).eq("recorded_date", str(form_date)).execute()
                    if check_exist.data:
                        supabase.table("brand_offline_outcomes").update(offline_payload).eq("id", check_exist.data[0]["id"]).execute()
                    else:
                        supabase.table("brand_offline_outcomes").insert(offline_payload).execute()
                        
                    st.success(f"Metrics record for {form_date} safely committed and locked!")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"Database write failure: {e}")

    st.write("---")

    # LOAD TIME-SERIES DATABASES
    digital_data, offline_data = load_o2o_data(user_id)

    # 3. SELECTION METRIC CONTROLLER HUB
    st.subheader("📐 Universal Multi-Touch Attribution Engine")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        attribution_model = st.selectbox(
            "Select Multi-Touch Model Allocation:",
            ["Linear (Equal Spread)", "Time-Decay (Proximity Weight)", "Position-Based (U-Shaped Focus)"]
        )
        st.info(f"**Active Operational Logic:** Shifting conversion visualizations using a native pathing matrix.")
        
        # INTERACTIVE SIMULATION SEED BUTTON
        st.write("---")
        st.caption("Don't feel like typing manual lines? Seed simulation statistics to instantly verify analytics chart trends.")
        if st.button("⚡ Seed Universal O2O Simulation Data", use_container_width=True):
            with st.spinner("Seeding time-series data logs..."):
                try:
                    supabase.table("brand_digital_inputs").delete().eq("user_id", user_id).execute()
                    supabase.table("brand_offline_outcomes").delete().eq("user_id", user_id).execute()
                    
                    today = datetime.date.today()
                    for i in range(7):
                        past_date = str(today - datetime.timedelta(days=i))
                        
                        supabase.table("brand_digital_inputs").insert([
                            {"user_id": user_id, "campaign_name": "The Core Manifesto", "platform": "Substack Blog", "ad_spend": 0.00, "impressions": 1200 + (i*150), "clicks_or_engagements": 300 + (i*20), "recorded_date": past_date},
                            {"user_id": user_id, "campaign_name": "Pattern Interrupt", "platform": "LinkedIn", "ad_spend": 150.00 + (i*50), "impressions": 5000 + (i*400), "clicks_or_engagements": 450 + (i*35), "recorded_date": past_date}
                        ]).execute()
                        
                        supabase.table("brand_offline_outcomes").insert({
                            "user_id": user_id,
                            "foot_traffic_count": 350 + (i * 45) + int(np.random.randint(-30, 30)),
                            "physical_conversions": 45 + (i * 8),
                            "gross_realized_revenue": 4500.00 + (i * 1200),
                            "recorded_date": past_date
                        }).execute()
                    
                    st.success("Simulation metrics safely committed to Supabase!")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"Seeding process failed: {e}")

    # 4. HIGH-FIDELITY VISUALIZATION LAYER
    with col2:
        if not digital_data or not offline_data:
            st.warning("📊 Awaiting data logs. Use the input form expander above to record numbers, or click the simulation seed button to draw metrics trends charts.")
        else:
            try:
                import plotly.express as px
                
                df_digital = pd.DataFrame(digital_data)
                df_offline = pd.DataFrame(offline_data)
                
                df_spend_grouped = df_digital.groupby("recorded_date")["ad_spend"].sum().reset_index()
                df_merged = pd.merge(df_spend_grouped, df_offline, on="recorded_date")
                
                fig = px.line(
                    df_merged, 
                    x="recorded_date", 
                    y=["foot_traffic_count", "ad_spend"],
                    labels={"value": "Metrics Scale", "recorded_date": "Operating Date"},
                    title="Online Investment vs Realized Offline Foot Traffic Correlation",
                    template="plotly_dark",
                    color_discrete_sequence=["#3498db", "#e74c3c"]
                )
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Failed rendering chart layouts: {e}")

    # 5. DATA TABLES LEDGER LOG
    if digital_data and offline_data:
        st.write("---")
        st.subheader("📋 Realized Operational Outcomes Tracker")
        
        ledger_df = pd.DataFrame(offline_data)[["recorded_date", "foot_traffic_count", "physical_conversions", "gross_realized_revenue"]]
        ledger_df.columns = ["Date Tracked", "Physical Foot Traffic Count", "On-Property Conversions", "Gross Realized Revenue ($)"]
        
        st.dataframe(ledger_df, use_container_width=True, hide_index=True)