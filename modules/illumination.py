import streamlit as st
import time
from utils.gemini_ai import get_soul_rebel_consultant
from utils.supabase_db import save_brand_data, load_brand_data

def run(user_id):
    st.title("✨ Phase 03: Illumination")
    st.caption("Forging the Strategic Individual: Subsection by Subsection.")
    st.write("---")
    
    # 1. INITIALIZE MASTER DATA & UI STATE
    db_data = load_brand_data(user_id)
    brand_data = db_data if db_data else {}

    # THE COGNITIVE BLUEPRINT: Explicitly mapping the exact weight, length, and rhythm of the document
    guide_structure = [
        {
            "id": "identity_big_idea",
            "label": "SECTION 1: BRAND IDENTITY",
            "sub": "Big Idea & Meaning",
            "blueprint": """
            - Structural Target: A single, rousing, evocative affirmation phrase (e.g., 'Beautiful Black Worlds') followed by a deep narrative dive spanning 7-8 expansive, deeply purposeful paragraphs.
            - Content Anatomy: Must break down the core 'Why'. It rejects industry disenfranchisement, centers dignity, highlights an 'inextinguishable light' within the target community, and frames the brand's work as a historical rallying call.
            - Tone: Poetic, soul-stirring, conversational yet authoritative, unapologetic, and emotionally charged.
            """
        },
        {
            "id": "identity_vision_mission",
            "label": "SECTION 1: BRAND IDENTITY",
            "sub": "Vision & Mission",
            "blueprint": """
            - Structural Target: 2 distinct sub-blocks. Each features a punchy, bold core declaration followed by a detailed, vivid 3-4 paragraph 'What it Means' narrative expansion.
            - Content Anatomy: 
               * Vision: A grand, global reimagining of public/private spaces (fewer fences, more green spaces, safe walkable realities) where the target audience unreservedly takes up space.
               * Mission: Framed as a industry-wide planning revolution meant to dismantle and radically transform inequitable systems marred by historical distrust.
            - Tone: Visionary, bold, revolutionary, and deeply disruptive.
            """
        },
        {
            "id": "process_methodology",
            "label": "SECTION 1: BRAND IDENTITY",
            "sub": "Our Transformation Process",
            "blueprint": """
            - Structural Target: A high-level introduction paragraph establishing a 3-way systemic change, followed by 3 robust, multi-paragraph conceptual deep-dives (each containing a core thesis statement and 2-3 paragraphs of operational reality).
            - Content Anatomy: Must clearly outline a three-pronged methodology for dismantling old structures (e.g., 1. Blueprinting/Rebuilding, 2. Advocating/Trust-building, 3. Informing/Knowledge-transfer). It explicitly details how the brand listens to the streets, curbs displacement, and educates systems for replicable global impact.
            - Tone: Strategic, defiant, highly structured, action-oriented, and fiercely protective of community agency.
            """
        },
        {
            "id": "anchors_culture_values",
            "label": "SECTION 1: BRAND IDENTITY",
            "sub": "Soul Anchors: Culture & Values",
            "blueprint": """
            - Structural Target: 1 introductory narrative paragraph establishing the heart of the culture, followed by 7 distinct, highly detailed value pillars. Each pillar must feature a bold name and a dedicated paragraph explaining its operational execution.
            - Content Anatomy: Replicate the depth of defining pillars like Humility, Diversity (not monolithic), Curiosity, Connection, Community Assets, Autonomy, and unapologetic cultural advocacy. It details exactly how these values show up in daily execution and collaborations.
            - Tone: Humble yet fiercely confident, deeply relational, sophisticated, and 'hella smart'.
            """
        },
        {
            "id": "anchors_beliefs_behaviours",
            "label": "SECTION 1: BRAND IDENTITY",
            "sub": "Soul Anchors: Beliefs & Behaviours",
            "blueprint": """
            - Structural Target: 2 comprehensive, bulleted manifestos. The 'Beliefs' section requires at least 10-12 authoritative statements. The 'Behaviours' section requires 6-8 strict, non-negotiable principle statements.
            - Content Anatomy: 
               * Beliefs: Must strictly begin with 'We believe...' (e.g., 'We believe that beauty and dignity should be the norm across the globe...').
               * Behaviours: Must strictly lead with operational imperatives and 'We always...' statements (e.g., 'We always listen and reflect...', 'We always lead with love and respect...').
            - Tone: Unwavering, non-negotiable, high-standard, programmatic, and clear.
            """
        },
        {
            "id": "positioning_1soul",
            "label": "SECTION 2: BRAND POSITIONING",
            "sub": "1Soul Statement & Meaning",
            "blueprint": """
            - Structural Target: A singular, definitive 1Soul corporate anchor sentence (e.g., 'At [Brand], we blueprint the world\'s most dignified spaces...'), followed by a powerful 5-6 paragraph 'What it Means' narrative.
            - Content Anatomy: Must position the brand as the absolute authority, ambassador, and provocateur of its industry. It explicitly details how present systems rob people of dignity, why the current framework cannot be fixed and must be dismantled, and how the brand breaks the status quo to establish an infinitely better standard.
            - Tone: Masterful, elite, authoritative, uncompromising, and highly strategic.
            """
        },
        {
            "id": "positioning_offerings",
            "label": "SECTION 2: BRAND POSITIONING",
            "sub": "Our Offering Matrix",
            "blueprint": """
            - Structural Target: 3 comprehensive, separate ecosystem deep-dives mapping out exact value propositions for Staff, Clients, and Communities. Each ecosystem must contain 1-2 narrative paragraphs followed by a clean, exhaustive list of specific sub-offerings.
            - Content Anatomy: Must break down long-term value:
               * Staff: Mentorship, residency pathways, turning careers into callings.
               * Clients: Strategic consulting, end-to-end advisory (grants, proposal requests, research).
               * Communities: Curbing displacement, space planning, mapping engagement models.
            - Tone: Generous, expert, professional, deeply supportive, and impact-driven.
            """
        },
        {
            "id": "positioning_audience",
            "label": "SECTION 2: BRAND POSITIONING",
            "sub": "Target Audience Profiles",
            "blueprint": """
            - Structural Target: 2 exhaustive, distinct profile breakdowns detailing 'Our Allies' and 'Our Target Partners/Staff', followed by a visceral, poetic raw-text list defining industry 'Harm'.
            - Content Anatomy: 
               * Allies: Profiles them as awake, able, inspirational, disruptive, and highly skilled individuals who share the brand values.
               * Target Partners: Profiles them as humble, hungry, and visionary.
               * Harm Breakdown: A literal, unvarnished list defining systemic failure (e.g., 'Harm is a food desert. Harm is a lack of inclusion. Harm is a failed design.').
            - Tone: Empathetic, descriptive, sharp, and raw when exposing systemic failures.
            """
        },
        {
            "id": "expression_slogan",
            "label": "SECTION 3: BRAND EXPRESSION",
            "sub": "Strategic Slogan & Manifest",
            "blueprint": """
            - Structural Target: A crisp, evocative core corporate slogan (e.g., 'Beauty in Black spaces'), backed by a 3-paragraph conceptual manifesto defining what that slogan actually delivers.
            - Content Anatomy: Elevates the slogan past a catchphrase. It defines the core outcome as a form of peace, security, holistic health, and generational wealth experienced by people dwelling in an environment purposefully built for them.
            - Tone: Inspiring, cinematic, premium, and visually descriptive.
            """
        },
        {
            "id": "expression_voice_personality",
            "label": "SECTION 3: BRAND EXPRESSION",
            "sub": "Brand Voice & Personality Archetype",
            "blueprint": """
            - Structural Target: 2 comprehensive segments detailing the verbal identity guidelines and the core behavioral character archetype.
            - Content Anatomy: 
               * Voice: Explicitly targets the 'Human, compelling, and hella smart' standard. Explains how every abandoned structure or challenge is viewed as an opportunity to ask what world can be realized here.
               * Personality: Solidifies the archetype (e.g., 'The Caring Catalyst')—defining a force that accelerates systemic healing, wholeness, and prosperity while balancing deep human empathy with elite technical competence.
            - Tone: Highly articulate, analytical of self, commanding, and profoundly loving.
            """
        },
        {
            "id": "ties_legacy",
            "label": "SECTION 4: SOUL TIES",
            "sub": "Brand Legacy",
            "blueprint": """
            - Structural Target: 1 high-level 'living legacy' statement paragraph, followed by 6 distinct, structured 'We want to be known for...' declarations.
            - Content Anatomy: Projects the brand's impact across generations and lifetimes. Outlines legacy targets as an excellent executor, a fearless leader, an elite advocate influencing policy, a generator of new knowledge, and an efficient mobilizer.
            - Tone: Historic, monumental, ancestral, and enduring.
            """
        },
        {
            "id": "ties_markers",
            "label": "SECTION 4: SOUL TIES",
            "sub": "Key Soul Markers (KPIs)",
            "blueprint": """
            - Structural Target: An exclusive framework consisting of 6-8 razor-sharp, introspective, and demanding metrics.
            - Content Anatomy: Every single metric must be written from the perspective of the brand or practitioner, framed strictly as an introspective 'Do I...' or 'Am I...' audit question (e.g., 'Do I pave the pathways necessary for my community to realize beauty in their spaces?', 'Am I there for and responsive to the communities that need us?').
            - Tone: Introspective, challenging, deeply accountable, and uncompromising.
            """
        }
    ]

    if "guide_idx" not in st.session_state:
        st.session_state.guide_idx = 0
    if "guide_content" not in st.session_state:
        st.session_state.guide_content = brand_data.get("soul_guide_parts", {})
    if "rev" not in st.session_state:
        st.session_state.rev = 0

    curr_idx = st.session_state.guide_idx

    # --- FINAL MASTER COMPILATION ---
    if curr_idx >= len(guide_structure):
        st.success("🎉 All sections meticulously forged! Your Master Soul Guide is complete.")
        full_text = "\n\n".join(st.session_state.guide_content.values())
        st.text_area("The Strategic Individual Master Document", value=full_text, height=600)
        
        if st.button("🗑️ Reset and Re-Illuminate"):
            st.session_state.guide_idx = 0
            st.session_state.guide_content = {}
            st.session_state.rev = 0
            st.rerun()
        return

    curr_sub = guide_structure[curr_idx]
    sub_key = curr_sub["id"]

    # 2. WORKSPACE LAYOUT
    col1, col2 = st.columns([3, 2])

    with col1:
        st.subheader(f"{curr_sub['label']}")
        st.info(f"**Forging Blueprint Element:** {curr_sub['sub']}")
        
        # A. INTUITIVE GENERATION (Using the deep blueprint + Soul Audit data)
        if sub_key not in st.session_state.guide_content:
            with st.spinner(f"Facilitator unearthing and drafting {curr_sub['sub']}..."):
                methodology = f"""
                ROLE: Godzspeed Soul Rebel Master Facilitator.
                TASK: Synthesize the Soul Audit discovery data into the specific subsection: '{curr_sub['sub']}'.
                
                STRICT STRUCTURAL AND TONAL BLUEPRINT:
                {curr_sub['blueprint']}
                
                VOICE STANDARD: You are a premium, highly sophisticated corporate strategist who speaks with a deeply human, compelling, and 'hella smart' rhythm. Lean into evocative, bold, narrative-driven phrasing. Avoid corporate fluff or generic marketing speak.
                
                GAP DETECTION:
                Analyze the provided Soul Audit data against the 'Structural Target' and 'Content Anatomy' rules. If the current audit data lacks the substance, narrative depth, or components required to build this specific section to full length, do not make up facts. 
                Instead, draft a strategic baseline framework, and immediately append a section titled '🚨 FACILITATOR INQUIRY' at the very bottom containing 3 highly targeted, thought-provoking, and confrontational strategic questions to force the user to provide the necessary fuel.
                """
                
                draft = get_soul_rebel_consultant(f"Draft {curr_sub['sub']}", methodology + "\n\nSOUL AUDIT DATA:\n" + str(brand_data))
                st.session_state.guide_content[sub_key] = draft

        # B. ANTI-SHADOWING WORKSPACE CONTAINER
        # The key version shifts via st.session_state.rev, forcing Streamlit to refresh the screen instantly on change
        workspace_key = f"area_{sub_key}_v{st.session_state.rev}"
        current_text = st.session_state.guide_content[sub_key]
        
        if "🚨 FACILITATOR INQUIRY" in current_text:
            st.warning("The Facilitator requires more raw fuel to reach the required length and depth standard.")

        edited_text = st.text_area(
            "Refine Strategic Individual Narrative:", 
            value=current_text, 
            height=450, 
            key=workspace_key
        )
        
        # Sync current manual text box modifications into state
        st.session_state.guide_content[sub_key] = edited_text

        # C. ADAPTIVE COLLABORATIVE SYNTHESIS ENGINE
        st.write("---")
        user_input = st.chat_input(f"Feed more raw details or answer inquiries for {curr_sub['sub']}...")
        
        if user_input:
            with st.spinner("Braiding and synthesizing your responses into the master blueprint..."):
                update_prompt = f"""
                ROLE: Godzspeed Soul Rebel Master Facilitator.
                TASK: Take the user's raw input, elevate it to our 'hella smart' and compelling brand voice, and surgically braid it into the EXISTING TEXT.
                
                STRICT INSTRUCTIONS:
                1. DO NOT shorten or overwrite the good structural text already established. Expand it.
                2. Maintain the specific blueprint parameters: {curr_sub['blueprint']}
                3. If the user's input successfully addresses a question inside the '🚨 FACILITATOR INQUIRY', remove that inquiry completely from the text.
                4. Output ONLY the complete, newly expanded narrative text block.
                
                EXISTING TEXT TO MODIFY:
                {edited_text}
                """
                
                new_narrative = get_soul_rebel_consultant(user_input, update_prompt)
                
                # Update state, tick the revision counter to wipe the field shadow, and reload
                st.session_state.guide_content[sub_key] = new_narrative
                st.session_state.rev += 1
                st.rerun()

    # 3. ROADMAP & GATEKEEPER PANEL (RIGHT COLUMN)
    with col2:
        st.subheader("📋 Soul Guide Architecture")
        for i, item in enumerate(guide_structure):
            if i < curr_idx:
                st.write(f"✅ {item['sub']}")
            elif i == curr_idx:
                st.markdown(f"**👉 {item['sub']}**")
            else:
                st.caption(f"⚪ {item['sub']}")
        
        st.write("---")
        
        # COMMIT GATEKEEPER
        is_light = "🚨 FACILITATOR INQUIRY" in edited_text
        if is_light:
            st.error("Gatekeeper Alert: This section cannot be committed until all '🚨 FACILITATOR INQUIRY' questions have been answered and removed.")
            
        if st.button("🔥 Commit & Advance Subsection", use_container_width=True, disabled=is_light):
            # Save validated piece to Supabase
            save_brand_data(user_id, edited_text, chamber=f"guide_part_{sub_key}")
            
            # Step forward, reset structural UI revision counter
            st.session_state.guide_idx += 1
            st.session_state.rev = 0
            st.rerun()