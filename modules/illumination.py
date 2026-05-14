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
    st.title("✨ Phase 03: Illumination")
    st.caption("Creating the ultimate reference, resource, and authority for your brand’s identity.")
    st.write("---")
    
    # 1. Sync State with Database
    db_data = load_brand_data(user_id)
    brand_data = db_data if db_data else {}
    
    # Update session state with the latest from DB
    st.session_state.final_soul_guide = brand_data.get("soul_guide", "")

    # 2. THE VALIDATION GATE
    # Check if the 4 foundation chambers are complete
    foundation_keys = ["purpus_summary", "brand_identity", "brand_experience", "brand_impact"]
    missing_chambers = [k for k in foundation_keys if not brand_data.get(k)]

    if missing_chambers:
        st.warning("⚠️ **Foundation Incomplete**")
        st.info("The Individual cannot be illuminated until the Soul Audit is finished. You have deleted or missed sections of your Soul Print.")
        
        # Display specifically what is missing to the user
        st.write("Please return to the Soul Sprint and complete:")
        for key in missing_chambers:
            st.write(f"- {key.replace('_', ' ').title()}")
            
        if st.button("⬅️ Return to Soul Sprint"):
            # In your main.py sidebar logic, the user can switch back, 
            # but this provides a direct psychological cue.
            st.info("Select '1. The Soul Sprint' in the sidebar.")
        return # STOP execution here so the guide doesn't show

    # 3. GENERATION PHASE (Only if foundation is complete but guide is empty)
    if not st.session_state.final_soul_guide:
        st.success("🎯 **Foundation Verified.** Your Soul Alignment is solid.")
        st.write("You are ready to unearth the Soul Guide—the bridge to your Brand Transformation.")
        
        if st.button("🔥 Illuminate the Soul Guide", use_container_width=True):
            with st.spinner("Synthesizing your Brand Individual..."):
                prompt = f"""
                You are a Master Soul Rebel Facilitator. Synthesize the Phase 03 Soul Guide.
                
                FOUNDATION DATA:
                - SOUL (PurpUS): {brand_data.get('purpus_summary')}
                - MIND (Identity): {brand_data.get('brand_identity')}
                - BODY (Experience): {brand_data.get('brand_experience')}
                - BODY (Impact): {brand_data.get('brand_impact')}
                
                Based on Godzspeed and JB Media principles, deliver a cohesive narrative covering:
                THE BIG IDEA, THE SOUL, THE MIND, and THE BODY (Impact Strategy).
                """
                guide = get_soul_rebel_consultant("Illuminate my Soul Guide.", prompt)
                
                st.session_state.final_soul_guide = guide
                save_brand_data(user_id, guide, chamber="soul_guide")
                st.rerun()
    
    # 4. THE WORKSPACE (Visible once generated and foundation is valid)
    else:
        st.subheader("📜 The Soul Guide (Master Document)")
        
        edited_text = st.text_area(
            "Finalize your Brand Individual:", 
            value=st.session_state.final_soul_guide, 
            height=500,
            key="guide_editor_field"
        )
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("💾 Save to Profile", use_container_width=True):
                save_brand_data(user_id, edited_text, chamber="soul_guide")
                st.success("Strategy Saved.")
        
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
            if st.button("🗑️ Reset & Re-Illuminate", use_container_width=True):
                save_brand_data(user_id, None, chamber="soul_guide") 
                st.session_state.final_soul_guide = ""
                st.rerun()

    st.write("---")
    with st.expander("🔍 View Source Foundation Data"):
        # We only show keys relevant to the foundation
        foundation_data = {k: v for k, v in brand_data.items() if k in foundation_keys}
        st.json(foundation_data)