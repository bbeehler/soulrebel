import streamlit as st
from utils.gemini_ai import get_soul_rebel_consultant
from utils.supabase_db import save_brand_data, load_brand_data
from fpdf import FPDF
import io

def generate_pdf(content):
    """Generates a PDF using fpdf2 and returns the byte data."""
    pdf = FPDF()
    pdf.add_page()
    
    # Using Helvetica as it is a standard core font (avoids encoding errors)
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "The Soul Guide: Strategic Individual", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Helvetica", size=12)
    # multi_cell handles line breaks and text wrapping automatically
    pdf.multi_cell(0, 10, content)
    
    # Output the PDF as bytes
    return pdf.output()

def run(user_id):
    st.title("✨ The Soul Guide")
    
    # 1. Sync State: Force Load from DB if session state is empty or cleared
    if "final_soul_guide" not in st.session_state or not st.session_state.final_soul_guide:
        db_data = load_brand_data(user_id)
        # Ensure db_data is a dict and get the soul_guide column
        st.session_state.final_soul_guide = db_data.get("soul_guide", "") if db_data else ""

    brand_data = st.session_state.get('brand_soul', {})

    # 2. GENERATION PHASE: Only visible if the guide is empty
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
                
                # Persist to state and database
                st.session_state.final_soul_guide = guide
                save_brand_data(user_id, guide, chamber="soul_guide")
                st.rerun()
    
    # 3. WORKSPACE PHASE: Visible once the guide is generated
    else:
        st.subheader("📜 Master Strategy Document")
        
        # Editable field for the user to refine the AI's synthesis
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
            # Generate PDF data on the fly based on current text area content
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
                # Clear state and null out the DB field
                st.session_state.final_soul_guide = ""
                save_brand_data(user_id, None, chamber="soul_guide") 
                st.warning("Soul Guide cleared.")
                st.rerun()

    st.write("---")
    with st.expander("🔍 View Raw Discovery Data"):
        st.json(brand_data)