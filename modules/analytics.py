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
                    
                    check_digital = supabase.table("brand_digital_inputs").select("id")\
                        .eq("user_id", user_id).eq("platform", log_platform).eq("recorded_date", str(form_date)).execute()
                        
                    if check_digital.data:
                        supabase.table("brand_digital_inputs").update(digital_payload).eq("id", check_digital.data[0]["id"]).execute()
                    else:
                        supabase.table("brand_digital_inputs").insert(digital_payload).execute()
                    
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

    # LOAD DATA STREAMS
    digital_data, offline_data = load_o2o_data(user_id)

    st.subheader("📐 Live Multi-Touch Attribution Engine")
    attribution_model = st.selectbox(
        "Select Active Multi-Touch Model Allocation Logic:",
        ["Linear (Equal Spread Across Path)", "Time-Decay (Proximity to Visit)", "Position-Based (U-Shaped First/Last Focus)"]
    )
    
    if not digital_data or not offline_data:
        st.warning("📊 Awaiting data entries. Drop daily numbers into the log form expander above to construct your visual dashboards.")
    else:
        try:
            import plotly.express as px
            import plotly.graph_objects as go
            
            df_digital = pd.DataFrame(digital_data)
            df_offline = pd.DataFrame(offline_data)
            
            df_spend_grouped = df_digital.groupby("recorded_date")["ad_spend"].sum().reset_index()
            df_merged = pd.merge(df_spend_grouped, df_offline, on="recorded_date").sort_values("recorded_date")

            # --- VISUAL PILLAR 1: DUAL-AXIS CORRELATION TIMELINE ---
            st.markdown("### 📈 Operational Pulse Timeline")
            fig_timeline = go.Figure()
            
            fig_timeline.add_trace(go.Scatter(
                x=df_merged["recorded_date"], y=df_merged["foot_traffic_count"],
                name="Physical Foot Traffic", mode="lines+markers",
                line=dict(color="#3498db", width=3),
                yaxis="y1"
            ))
            
            fig_timeline.add_trace(go.Scatter(
                x=df_merged["recorded_date"], y=df_merged["ad_spend"],
                name="Digital Ad Spend ($)", mode="lines+markers",
                line=dict(color="#e74c3c", width=3, dash="dot"),
                yaxis="y2"
            ))
            
            # FIXED: Migrated raw 'titlefont' properties to unified title nested font dictionaries
            fig_timeline.update_layout(
                title="Digital Marketing Capital Surge vs Spatial Foot Traffic Correlation",
                template="plotly_dark",
                hovermode="x unified",
                yaxis=dict(
                    title=dict(text="Physical Foot Traffic (Persons)", font=dict(color="#3498db")), 
                    tickfont=dict(color="#3498db")
                ),
                yaxis2=dict(
                    title=dict(text="Digital Ad Spend ($)", font=dict(color="#e74c3c")), 
                    tickfont=dict(color="#e74c3c"), 
                    anchor="x", overlaying="y", side="right"
                ),
                legend=dict(x=0.01, y=0.99, bgcolor="rgba(0,0,0,0.5)")
            )
            st.plotly_chart(fig_timeline, use_container_width=True)
            
            st.write("---")
            
            # --- VISUAL PILLAR 2: SHARE OF VOICE DONUT ANALYSIS ---
            st.markdown("### 🎯 Distribution Dynamics")
            v_col1, v_col2 = st.columns(2)
            
            df_platform_totals = df_digital.groupby("platform")[["ad_spend", "clicks_or_engagements"]].sum().reset_index()
            
            with v_col1:
                fig_spend_share = px.pie(
                    df_platform_totals, values="ad_spend", names="platform", hole=0.5,
                    title="Capital Investment Allocation per Channel",
                    template="plotly_dark", color_discrete_sequence=px.colors.qualitative.Pastel
                )
                fig_spend_share.update_traces(textposition="inside", textinfo="percent+label")
                st.plotly_chart(fig_spend_share, use_container_width=True)
                
            with v_col2:
                fig_click_share = px.pie(
                    df_platform_totals, values="clicks_or_engagements", names="platform", hole=0.5,
                    title="Realized Audience Engagement Share per Channel",
                    template="plotly_dark", color_discrete_sequence=px.colors.qualitative.Safe
                )
                fig_click_share.update_traces(textposition="inside", textinfo="percent+label")
                st.plotly_chart(fig_click_share, use_container_width=True)

            st.write("---")
            
            # --- VISUAL PILLAR 3: CROSS-CHANNEL ATTRITION FUNNEL ---
            st.markdown("### 🌪️ StratOS Stratified Conversion Funnel")
            
            total_impressions = df_digital["impressions"].sum()
            total_engagements = df_digital["clicks_or_engagements"].sum()
            total_conversions = df_offline["physical_conversions"].sum()
            
            funnel_data = dict(
                number=[total_impressions, total_engagements, total_conversions],
                stage=["Digital Impressions Served", "Active Digital Engagements", "Realized Physical Spatial Conversions"]
            )
            
            fig_funnel = px.bar(
                funnel_data, x="number", y="stage", orientation="h",
                title="Universal StratOS Cross-Channel Conversion Pipeline Volume",
                labels={"number": "Aggregate Volume Count", "stage": "Funnel Phase"},
                template="plotly_dark",
                color="stage", color_discrete_sequence=["#9b59b6", "#34495e", "#2ecc71"]
            )
            fig_funnel.update_layout(showlegend=False)
            st.plotly_chart(fig_funnel, use_container_width=True)

        except Exception as e:
            st.error(f"Failed rendering optimized charts matrix: {e}")

    # 4. CHANNELS LEDGER TRACKER LOGS
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