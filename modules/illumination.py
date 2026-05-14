import streamlit as st
from utils.gemini_ai import get_soul_rebel_consultant
from utils.supabase_db import save_brand_data, load_brand_data
from fpdf import FPDF

def clean_unicode(text):
    if not text: return ""
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
    st.title("✨ The Soul Guide")
    
    if "final_soul_guide" not in st.session_state or not st.session_state.final_soul_guide:
        db_data = load_brand_data(user_id)
        st.session_state.final_soul_guide = db_data.get("soul_guide", "") if db_data else ""

    brand_data = st.session_state.get('brand_soul', {})

    if not st.session_state.final_soul_guide:
        st.info("The Soul Sprint is complete. Ready to amplify your impact?")
        if st.button("🔥 Illuminate the Soul Guide", use_container_width=True):
            with st.spinner("Synthesizing High-Impact Strategy..."):
                # INTEGRATED PROMPT: Godzspeed + JB Media Group
                prompt = f"""
                You are a Master Strategic Consultant. You are weaving a 'Soul Guide' using:
                1. The Godzspeed Method (Soul, Mind, Body).
                2. The JB Media Group Impact Philosophy (Storytelling for Growth & Social Impact).
                
                ANATOMY INPUTS:
                - SOUL: {brand_data.get('purpus_summary')}
                - MIND: {brand_data.get('brand_identity')}
                - BODY (Ritual): {brand_data.get('brand_experience')}
                - BODY (Impact): {brand_data.get('brand_impact')}
                
                SYNTHESIS REQUIREMENTS:
                - THE BIG IDEA: Craft a singular, visceral hook.
                - THE SOUL: Define the 'Transcendental Fire'. How does this brand humanize its mission?
                - THE MIND: Strategic Persona. Define the 'Voice of Authority' and how it shares its story to attract a community.
                - THE BODY (IMPACT STRATEGY): Don't just list goals. Using JB Media principles, describe how this brand creates 'Bigger Impact' through digital reach, community engagement, and solving urgent community problems.
                
                Format this as a professional, high-level Strategic Bible.
                """
                guide = get_soul_rebel_consultant("Illuminate my Soul Guide.", prompt)
                
                st.session_state.final_soul_guide = guide
                save_brand_data(user_id, guide, chamber="soul_guide")
                st.rerun()
    
    else:
        st.subheader("📜 Master Strategy Document")
        
        edited_text = st.text_area(
            "Refine your Brand Soul & Impact Strategy:", 
            value=st.session_state.final_soul_guide, 
            height=550,
            key="guide_editor_field"
        )
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("💾 Save to Profile", use_container_width=True):
                st.session_state.final_soul_guide = edited_text
                save_brand_data(user_id, edited_text, chamber="soul_guide")
                st.success("Impact Strategy Saved.")
        
        with col2:
            try:
                pdf_bytes = generate_pdf(edited_text)
                st.download_button(
                    label="📄 Download Soul Guide PDF",
                    data=pdf_bytes,
                    file_name="Soul_Guide_Impact_Strategy.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"PDF Error: {e}")
            
        with col3:
            if st.button("🗑️ Delete & Reset", use_container_width=True):
                st.session_state.final_soul_guide = ""
                save_brand_data(user_id, None, chamber="soul_guide") 
                st.warning("Guide cleared.")
                st.rerun()

    st.write("---")
    with st.expander("🔍 View Discovery Context"):
        st.json(brand_data)