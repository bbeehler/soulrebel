import streamlit as st
from utils.gemini_ai import get_soul_rebel_consultant
from utils.supabase_db import save_brand_data, load_brand_data
from fpdf import FPDF

def clean_unicode(text):
    if not text: 
        return ""
    replacements = {
        "\u2013": "-", "\u2014": "-", "\u2018": "'", "\u2019": "'",
        "\u201c": '"', "\u201d": '"', "\u2022": "*", "\u2026": "...",
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    return text.encode('latin-1', 'ignore').decode('latin-1')

def generate_pdf(content):
    safe_content = clean_unicode(content)
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "The Soul Guide: Strategic Individual", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Helvetica", size=12)
    pdf.multi_cell(0, 10, safe_content)
    return bytes(pdf.output())

def run(user_id):
    st.title("✨ Phase 03: Illumination")
    st.caption("To illuminate means to bring to light. We are unearthing and igniting your purpose-driven brand.")
    st.write("---")
    
    db_data = load_brand_data(user_id)
    brand_data = db_data if db_data else {}
    st.session_state.final_soul_guide = brand_data.get("soul_guide", "")

    # 1. THE VALIDATION GATE
    foundation_keys = ["purpus_summary", "brand_identity", "brand_experience", "brand_impact"]
    missing_chambers = [k for k in foundation_keys if not brand_data.get(k)]

    if missing_chambers:
        st.warning("⚠️ **Foundation Incomplete**")
        st.info("The Soul Guide requires a solidified foundation. We must determine who you are before we bring it to light.")
        for key in missing_chambers:
            st.write(f"- {key.replace('_', ' ').title()}")
        if st.button("⬅️ Return to Phase 02: Foundation", use_container_width=True):
            st.session_state.target_page = "1. The Soul Sprint"
            st.rerun()
        return

    # 2. GENERATION PHASE
    if not st.session_state.final_soul_guide:
        st.success("🎯 **Foundation Verified.** Ready to unearth the soul.")
        if st.button("🔥 Illuminate the Soul Guide", use_container_width=True):
            with st.spinner("Bringing your identity to light..."):
                # CEO-ALIGNED SYNTHESIS PROMPT
                prompt = f"""
                You are a Master Soul Rebel Facilitator. You are in Phase 03: Illumination.
                Your goal is to unearth, illuminate, and ignite the soul of this purpose-driven brand.
                
                FOUNDATION DATA:
                - SOUL (PurpUS): {brand_data.get('purpus_summary')}
                - MIND (Identity): {brand_data.get('brand_identity')}
                - BODY (Experience): {brand_data.get('brand_experience')}
                - BODY (Impact): {brand_data.get('brand_impact')}
                
                ILLUMINATION STRATEGY:
                1. THE IDENTITY: Bring to light the substance and value of this soul.
                2. WORDS & PHILOSOPHIES: Find the language necessary to carry meaning for both internal people and external audiences. 
                3. BRAND EXPERIENCE: Craft the brand's tone, personality, and the way it communicates.
                4. THE BIG IDEA: Leverage the soul to communicate with audiences, putting their focus first so they understand why you are valuable in their lives. 
                5. PREPARE FOR TRANSFORMATION: Ensure this identity is ready to be implemented and activated so it becomes real.
                
                Deliver a cohesive narrative that establishes this brand as a 'Strategic Individual.'
                """
                guide = get_soul_rebel_consultant("Illuminate my Soul Guide.", prompt)
                st.session_state.final_soul_guide = guide
                save_brand_data(user_id, guide, chamber="soul_guide")
                st.rerun()
    
    # 3. THE WORKSPACE
    else:
        st.subheader("📜 The Soul Guide (Master Document)")
        edited_text = st.text_area(
            "Finalize the words and philosophies that carry your meaning:", 
            value=st.session_state.final_soul_guide, 
            height=500,
            key="guide_editor_field"
        )
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("💾 Save Strategy", use_container_width=True):
                save_brand_data(user_id, edited_text, chamber="soul_guide")
                st.success("Soul Guide Updated.")
        with col2:
            try:
                pdf_bytes = generate_pdf(edited_text)
                st.download_button(
                    label="📄 Download PDF",
                    data=pdf_bytes,
                    file_name="Godzspeed_Soul_Guide.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"PDF Error: {e}")
        with col3:
            if st.button("🗑️ Re-Illuminate", use_container_width=True):
                save_brand_data(user_id, None, chamber="soul_guide") 
                st.session_state.final_soul_guide = ""
                st.rerun()

    st.write("---")
    with st.expander("🔍 View Foundation Source"):
        foundation_data = {k: v for k, v in brand_data.items() if k in foundation_keys}
        st.json(foundation_data)