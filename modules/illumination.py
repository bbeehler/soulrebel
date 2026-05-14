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
    st.title("✨ Illumination")
    st.caption("The Soul Guide: The ultimate reference, resource, and authority for your brand’s identity.")
    st.write("---")
    
    db_data = load_brand_data(user_id)
    brand_data = db_data if db_data else {}
    st.session_state.final_soul_guide = brand_data.get("soul_guide", "")

    # 1. THE VALIDATION GATE
    foundation_keys = ["purpus_summary", "brand_identity", "brand_experience", "brand_impact"]
    missing_chambers = [k for k in foundation_keys if not brand_data.get(k)]

    if missing_chambers:
        st.warning("⚠️ **Foundation Incomplete**")
        st.info("The Soul Guide requires a solidified foundation. Please complete your Soul Audit.")
        for key in missing_chambers:
            st.write(f"- {key.replace('_', ' ').title()}")
        if st.button("⬅️ Return to The Soul Sprint", use_container_width=True):
            st.session_state.target_page = "1. The Soul Sprint"
            st.rerun()
        return

    # 2. GENERATION PHASE
    if not st.session_state.final_soul_guide:
        st.success("🎯 **Foundation Verified.** Soul Alignment is active.")
        if st.button("🔥 Illuminate the Soul Guide", use_container_width=True):
            with st.spinner("Synthesizing the Strategic Individual..."):
                # HIGH-IMPACT SYNTHESIS PROMPT
                prompt = f"""
                You are a Master Soul Rebel Facilitator. Synthesize the Phase 03 Soul Guide (The Strategic Bible).
                
                ANATOMY DATA:
                - SOUL (PurpUS): {brand_data.get('purpus_summary')}
                - MIND (Identity): {brand_data.get('brand_identity')}
                - BODY (Experience): {brand_data.get('brand_experience')}
                - BODY (Impact): {brand_data.get('brand_impact')}
                
                STRATEGIC FRAMEWORK:
                1. THE INDIVIDUAL: Transform these inputs into a singular, living brand persona.
                2. THE CORE ETHOS: Define the shared PurpUS that rallies staff and clients.
                3. REVENUE & ENGAGE: How does this identity deepen bonds and increase business revenue?
                4. IMPACT POSITIONING: How does this brand solver community problems?
                
                Deliver a cohesive, high-authority narrative for growth and brand affinity.
                """
                guide = get_soul_rebel_consultant("Illuminate my Soul Guide.", prompt)
                st.session_state.final_soul_guide = guide
                save_brand_data(user_id, guide, chamber="soul_guide")
                st.rerun()
    
    # 3. THE WORKSPACE
    else:
        st.subheader("📜 The Soul Guide (Master Document)")
        edited_text = st.text_area(
            "Refine your Strategic Individual:", 
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