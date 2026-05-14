import streamlit as st
from utils.gemini_ai import get_soul_rebel_consultant
from utils.supabase_db import save_brand_data, load_brand_data
from fpdf import FPDF
import io

def generate_pdf(content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(40, 10, "The Soul Guide: Strategic Individual")
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    # Multi_cell handles text wrapping for long strategy content
    pdf.multi_cell(0, 10, content)
    return pdf.output(dest='S')

def run(user_id):
    st.title("✨ The Soul Guide")
    
    # 1. Force Load from DB if session state is empty
    if "final_soul_guide" not in st.session_state or not st.session_state.final_soul_guide:
        db_data = load_brand_data(user_id)
        st.session_state.final_soul_guide = db_data.get("soul_guide", "")

    brand_data = st.session_state.get('brand_soul', {})

    # 2. GENERATION PHASE (Only visible if no guide exists)
    if not st.session_state.final_soul_guide:
        st.info("Your 4 chambers are locked. Ready to weave them into the Soul Guide?")
        if st.button("🔥 Illuminate the Soul Guide", use_container_width=True):
            with st.spinner("Synthesizing..."):
                prompt = f"""
                Synthesize a Godzspeed Soul Guide based on:
                SOUL: {brand_data.get('purpus_summary')}
                MIND: {brand_data.get('brand_identity')}
                BODY (Experience): {brand_data.get('brand_experience')}
                BODY (Impact): {brand_data.get('brand_impact')}
                """
                guide = get_soul_rebel_consultant("Synthesize my Soul Guide.", prompt)
                
                # Persist
                st.session_state.final_soul_guide = guide
                save_brand_data(user_id, guide, chamber="soul_guide")
                st.rerun()
    
    # 3. EDIT, SAVE, DELETE & PDF PHASE (Visible once guide exists)
    else:
        st.subheader("📜 Master Strategy Document")
        
        # This is the field you wanted
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
                st.success("Soul Guide Updated in Database.")
        
        with col2:
            # PDF Generation logic
            pdf_data = generate_pdf(edited_text)
            st.download_button(
                label="📄 Download Soul Guide PDF",
                data=pdf_data,
                file_name="Soul_Guide_Strategy.pdf",
                mime="application/pdf",
                use_container_width=True
            )
            
        with col3:
            if st.button("🗑️ Delete & Reset", use_container_width=True):
                st.session_state.final_soul_guide = ""
                save_brand_data(user_id, None, chamber="soul_guide") # Null out the DB field
                st.warning("Guide cleared. You can now re-illuminate.")
                st.rerun()

    st.write("---")
    with st.expander("🔍 View Raw Chamber Data"):
        st.json(brand_data)