import streamlit as st
from utils.gemini_ai import get_soul_rebel_consultant
from utils.supabase_db import save_brand_data, load_brand_data
from fpdf import FPDF
import io

def clean_unicode(text):
    """
    Replaces common Unicode characters that break standard PDF fonts
    with their ASCII equivalents to prevent encoding errors.
    """
    if not text:
        return ""
    replacements = {
        "\u2013": "-", # en-dash
        "\u2014": "-", # em-dash
        "\u2018": "'", # left single quote
        "\u2019": "'", # right single quote
        "\u201c": '"', # left double quote
        "\u201d": '"', # right double quote
        "\u2022": "*", # bullet point
        "\u2026": "...", # ellipsis
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    
    # Final safety net: encode to latin-1 and ignore anything else remaining
    return text.encode('latin-1', 'ignore').decode('latin-1')

def generate_pdf(content):
    """Generates a PDF safely and converts the output to standard bytes."""
    safe_content = clean_unicode(content)
    
    pdf = FPDF()
    pdf.add_page()
    
    # Header
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "The Soul Guide: Strategic Individual", ln=True, align='C')
    pdf.ln(10)
    
    # Body
    pdf.set_font("Helvetica", size=12)
    pdf.multi_cell(0, 10, safe_content)
    
    # pdf.output() returns a bytearray in newer fpdf2 versions.
    # bytes() converts that bytearray into the standard binary format Streamlit expects.
    return bytes(pdf.output())

def run(user_id):
    st.title("✨ The Soul Guide")
    
    # 1. Sync State: Load from DB if session state is empty
    if "final_soul_guide" not in st.session_state or not st.session_state.final_soul_guide:
        db_data = load_brand_data(user_id)
        st.session_state.final_soul_guide = db_data.get("soul_guide", "") if db_data else ""

    brand_data = st.session_state.get('brand_soul', {})

    # 2. GENERATION PHASE
    if not st.session_state.final_soul_guide:
        st.info("Your 4 chambers are locked. Ready to weave them into the Soul Guide?")
        if st.button("🔥 Illuminate the Soul Guide", use_container_width=True):
            with st.spinner("Synthesizing Strategy..."):
                prompt = f"""
                Synthesize a Godzspeed Soul Guide based on the following brand anatomy:
                
                SOUL (PurpUS): {brand_data.get('purpus_summary')}
                MIND (Identity): {brand_data.get('brand_identity')}
                BODY (Experience): {brand_data.get('brand_experience')}
                BODY (Impact): {brand_data.get('brand_impact')}
                
                Ensure the response is a cohesive strategic narrative.
                """
                guide = get_soul_rebel_consultant("Synthesize my Soul Guide.", prompt)
                
                st.session_state.final_soul_guide = guide
                save_brand_data(user_id, guide, chamber="soul_guide")
                st.rerun()
    
    # 3. WORKSPACE PHASE
    else:
        st.subheader("📜 Master Strategy Document")
        
        edited_text = st.text_area(
            "Refine your Brand Soul:", 
            value=st.session_state.final_soul_guide, 
            height=500,
            key="guide_editor_field"
        )
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("💾 Save to Profile", use_container_width=True):
                st.session_state.final_soul_guide = edited_text
                save_brand_data(user_id, edited_text, chamber="soul_guide")
                st.success("Soul Guide Saved.")
        
        with col2:
            try:
                pdf_bytes = generate_pdf(edited_text)
                st.download_button(
                    label="📄 Download Soul Guide PDF",
                    data=pdf_bytes,
                    file_name="Soul_Guide_Strategy.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"PDF Generation Error: {e}")
            
        with col3:
            if st.button("🗑️ Delete & Reset", use_container_width=True):
                st.session_state.final_soul_guide = ""
                save_brand_data(user_id, None, chamber="soul_guide") 
                st.warning("Soul Guide cleared.")
                st.rerun()

    st.write("---")
    with st.expander("🔍 View Raw Discovery Data"):
        st.json(brand_data)