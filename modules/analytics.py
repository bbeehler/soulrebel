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
    """Computes an execution grade based on the ratio of compliant passed assets."""
    try:
        content_items = supabase.table("brand_content_items").select("status", "guardian_notes").eq("user_id", user_id).execute()
        if not content_items.data:
            return "N/A", "No assets have been passed through the Brand Guardian gate yet.", "#808080"
            
        total_assets = len(content_items.data)
        passed_assets = sum(1 for item in content_items.data if item['status'] == 'approved_for_publishing' or (item['guardian_notes'] and "SCORE: PASS" in item['guardian_notes']))
        
        compliance_ratio = (passed_assets / total_assets) * 100
        
        if compliance_ratio >= 90:
            return "A", f"Exceptional Soul Alignment ({compliance_ratio:.1f}%).", "#2ecc71"
        elif compliance_ratio >= 80:
            return "B", f"Strong Soul Alignment ({compliance_ratio:.1f}%).", "#3498db"
        elif compliance_ratio >= 70:
            return "C", f"Compromised Soul Alignment ({compliance_ratio:.1f}%).", "#f1c40f"
        elif compliance_ratio >= 60:
            return "D", f"Critical Shift Flagged ({compliance_ratio:.1f}%).", "#e67e22"
        else:
            return "F", f"Systemic Shadowing Violation ({compliance_ratio:.1f}%).", "#e74c3c"
    except Exception:
        return "N/A", "Enforcement logging tracking unavailable.", "#808080"

def run(user_id):
    st.title("📊 Phase 05: O2O Attribution Analytics")
    st.caption("The Strategic Verification Center: Linking Digital Engagement to Physical Spatial Conversions.")
    st.write("---")

    # 1. LIVE BRAND GUARDIAN ENFORCEMENT AUDIT
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

    # 2. THE MANUAL OPERATIONS DATA ENTRY PANEL
    with st.expander("📥 Manual Operations Log Entry Form", expanded=False):
        st.markdown("### Log Daily Performance Metrics")
        st.caption("Record inputs per channel and real-world results for a specific business day.")
        
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
                    digital_payload = {
                        "user_id": user_id, "campaign_name": log_campaign, "platform": log_platform,
                        "ad_spend": log_spend, "impressions": log_impressions, "clicks_or_engagements": log_clicks,
                        "recorded_date": str(form_date)
                    }
                    offline_payload = {
                        "user_id": user_id, "foot_traffic_count": log_traffic, "physical_conversions": log_conversions,
                        "gross_realized_revenue": log_revenue, "recorded_date": str(form_date)
                    }
                    
                    # --- FIX 1: CHANNEL ISOLATION UPSERT ENGINE ---
                    # Check if this user already logged an entry for this EXACT platform on this EXACT day
                    check_digital = supabase.table("brand_digital_inputs").select("id")\
                        .eq("user_id", user_id).eq("platform", log_platform).eq("recorded_date", str(form_date)).execute()
                        
                    if check_digital.data:
                        supabase.table("brand_digital_inputs").update(digital_payload).eq("id", check_digital.data[0]["id"]).execute()
                    else:
                        supabase.table("brand_digital_inputs").insert(digital_payload).execute()
                    
                    # Save offline outcomes for the day
                    check_offline = supabase.table("brand_offline_outcomes").select("id").eq("user_id", user_id).eq("recorded_date", str(form_date)).execute()
                    if check_offline.data:
                        supabase.table("brand_offline_outcomes").update(offline_payload).eq("id", check_offline.data[0]["id"]).execute()
                    else:
                        supabase.table("brand_offline_outcomes").insert(offline_payload).execute()
                        
                    st.success(f"Metrics record for {log_platform} on {form_date} safely saved!")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"Database write failure: {e}")

    st.write("---")

    # LOAD TIME-SERIES DATABASES
    digital_data, offline_data = load_o2o_data(user_id)

    # 3. SELECTION METRIC CONTROLLER HUB & VISUALIZATION LAYER
    st.subheader("📐 Universal Multi-Touch Attribution Engine")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        attribution_model = st.selectbox(
            "Select Multi-Touch Model Allocation:",
            ["Linear (Equal Spread)", "Time-Decay (Proximity Weight)", "Position-Based (U-Shaped Focus)"]
        )
        st.info(f"**Active Operational Logic:** Shifting conversion visualizations using a native pathing matrix.")

    with col2:
        if not digital_data or not offline_data:
            st.warning("📊 Awaiting data logs. Use the input form expander above to record day-to-day metrics and draw your charts.")
        else:
            try:
                import plotly.express as px
                
                df_digital = pd.DataFrame(digital_data)
                df_offline = pd.DataFrame(offline_data)
                
                # --- FIX 2: CHANNELS ACCUMULATE INSIDE CHART MERGE ---
                df_spend_grouped = df_digital.groupby("recorded_date")["ad_spend"].sum().reset_index()
                df_merged = pd.merge(df_spend_grouped, df_offline, on="recorded_date")
                
                fig = px.line(
                    df_merged, 
                    x="recorded_date", 
                    y=["foot_traffic_count", "ad_spend"],
                    labels={"value": "Metrics Scale", "recorded_date": "Operating Date"},
                    title="Total Online Investment vs Realized Offline Foot Traffic Correlation",
                    template="plotly_dark",
                    color_discrete_sequence=["#3498db", "#e74c3c"]
                )
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Failed rendering chart layouts: {e}")

    # 4. CHANNELS LEDGER TRACKER LOG (FIX 3: DYNAMIC COMPARATIVE LOOKUP)
    if digital_data and offline_data:
        st.write("---")
        st.subheader("📋 Comprehensive Digital Inputs Ledger")
        df_dig_ledger = pd.DataFrame(digital_data)[["recorded_date", "campaign_name", "platform", "ad_spend", "impressions", "clicks_or_engagements"]]
        df_dig_ledger.columns = ["Date Tracked", "Campaign Name", "Platform / Channel", "Ad Spend ($)", "Impressions", "Clicks / Engagement"]
        st.dataframe(df_dig_ledger, use_container_width=True, hide_index=True)

        st.subheader("📋 Realized Offline Outcomes Tracker")
        ledger_df = pd.DataFrame(offline_data)[["recorded_date", "foot_traffic_count", "physical_conversions", "gross_realized_revenue"]]
        ledger_df.columns = ["Date Tracked", "Physical Foot Traffic Count", "On-Property Conversions", "Gross Realized Revenue ($)"]
        st.dataframe(ledger_df, use_container_width=True, hide_index=True)