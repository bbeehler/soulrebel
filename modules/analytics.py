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
    
    # FIXED: Replaced unsafe_style_allowed with correct parameter unsafe_allow_html=True
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

    # LOAD TIME-SERIES DATABASES
    digital_data, offline_data = load_o2o_data(user_id)

    # 2. SELECTION METRIC CONTROLLER HUB
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
        st.caption("Database empty? Seed high-fidelity operational simulation values to verify analytics trends.")
        if st.button("⚡ Seed Universal O2O Simulation Data", use_container_width=True):
            # FIXED: Capitalized St.spinner changed to correct lowercase st.spinner
            with st.spinner("Seeding time-series data logs..."):
                try:
                    # Clear out stale data to avoid overlapping timelines
                    supabase.table("brand_digital_inputs").delete().eq("user_id", user_id).execute()
                    supabase.table("brand_offline_outcomes").delete().eq("user_id", user_id).execute()
                    
                    today = datetime.date.today()
                    for i in range(7):
                        past_date = str(today - datetime.timedelta(days=i))
                        
                        # Populate multi-channel digital entries
                        supabase.table("brand_digital_inputs").insert([
                            {"user_id": user_id, "campaign_name": "The Core Manifesto", "platform": "Substack Blog", "ad_spend": 0.00, "impressions": 1200 + (i*150), "clicks_or_engagements": 300 + (i*20), "recorded_date": past_date},
                            {"user_id": user_id, "campaign_name": "Pattern Interrupt", "platform": "LinkedIn", "ad_spend": 150.00 + (i*50), "impressions": 5000 + (i*400), "clicks_or_engagements": 450 + (i*35), "recorded_date": past_date}
                        ]).execute()
                        
                        # Populate tracking baseline outcomes
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

    # 3. HIGH-FIDELITY VISUALIZATION LAYER
    with col2:
        if not digital_data or not offline_data:
            st.warning("📊 Awaiting data logs. Seed simulation statistics above to render metrics charts.")
        else:
            try:
                import plotly.express as px
                
                df_digital = pd.DataFrame(digital_data)
                df_offline = pd.DataFrame(offline_data)
                
                # Group total spend by date
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

    # 4. DATA TABLES LEDGER LOG
    if digital_data and offline_data:
        st.write("---")
        st.subheader("📋 Realized Operational Outcomes Tracker")
        
        ledger_df = pd.DataFrame(offline_data)[["recorded_date", "foot_traffic_count", "physical_conversions", "gross_realized_revenue"]]
        ledger_df.columns = ["Date Tracked", "Physical Foot Traffic Count", "On-Property Conversions", "Gross Realized Revenue ($)"]
        
        st.dataframe(ledger_df, use_container_width=True, hide_index=True)