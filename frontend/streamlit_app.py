import streamlit as st
import httpx
import os
import uuid
from pathlib import Path

# Configure Page
st.set_page_config(
    page_title="Vasu's Digital Twin",
    page_icon="👤",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Premium Styling
st.markdown("""
<style>
    /* Styling for glassmorphic elements and clean dark theme details */
    .stApp {
        background-color: #0d0f12;
        color: #e2e8f0;
        font-family: 'Inter', sans-serif;
    }
    .main-title {
        background: linear-gradient(90deg, #3b82f6 0%, #8b5cf6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 3rem;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        color: #94a3b8;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .card {
        background: rgba(30, 41, 59, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        backdrop-filter: blur(8px);
    }
    .metric-title {
        color: #38bdf8;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.25rem;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #f8fafc;
    }
    .source-tag {
        display: inline-block;
        background: rgba(59, 130, 246, 0.15);
        color: #60a5fa;
        border: 1px solid rgba(59, 130, 246, 0.3);
        border-radius: 4px;
        padding: 0.2rem 0.5rem;
        font-size: 0.75rem;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# API Configuration
API_BASE_URL = "http://127.0.0.1:8000"

# Initialize Session States
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "last_explainability" not in st.session_state:
    st.session_state.last_explainability = None
if "synthesized_audio" not in st.session_state:
    st.session_state.synthesized_audio = None

# Sidebar Configuration
with st.sidebar:
    st.markdown("<h2 style='color: #60a5fa;'>⚙️ Twin Control Panel</h2>", unsafe_allow_html=True)
    
    # Engine Settings
    st.subheader("Module Settings")
    use_rag = st.checkbox("Enable RAG (Resume/Projects Knowledge)", value=True)
    use_memory = st.checkbox("Enable Long-Term SQLite Memory", value=True)
    voice_response = st.checkbox("Synthesize Cloned Voice Response", value=True)
    
    st.markdown("---")
    
    # Document Upload Dashboard
    st.subheader("📄 Knowledge Ingestion")
    doc_category = st.selectbox(
        "Upload Directory", 
        ["resume", "projects", "certificates", "notes", "linkedin"]
    )
    uploaded_file = st.file_uploader("Choose a document", type=["txt", "md", "pdf"])
    
    if uploaded_file is not None:
        if st.button("Index Document", use_container_width=True):
            with st.spinner("Processing & embedding document..."):
                try:
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    params = {"category": doc_category}
                    r = httpx.post(f"{API_BASE_URL}/documents/upload", files=files, params=params, timeout=None)
                    if r.status_code == 200:
                        st.success(f"Indexed: {uploaded_file.name}")
                        # Refresh documents list
                        st.rerun()
                    else:
                        try:
                            error_detail = r.json().get('detail', 'Unknown error')
                        except Exception:
                            error_detail = r.text
                        st.error(f"Error {r.status_code}: {error_detail}")
                except Exception as e:
                    st.error(f"Failed to connect to API: {str(e)}")

    st.markdown("---")

    # Document manager
    st.subheader("📚 Indexed Documents")
    try:
        r = httpx.get(f"{API_BASE_URL}/documents/list")
        if r.status_code == 200:
            docs = r.json().get("documents", [])
            if not docs:
                st.info("No documents uploaded yet.")
            else:
                for d in docs[:5]: # Show first 5
                    st.markdown(f"📎 `{d['category']}`: {d['name']}")
                if len(docs) > 5:
                    st.markdown(f"*And {len(docs) - 5} more...*")
        else:
            st.error("Failed to list indexed documents.")
    except Exception:
        st.warning("Start API server to list documents.")

# Main Application Layout
st.markdown("<h1 class='main-title'>👤 Digital Human Twin</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Vasu's Personalized AI Replica - Context-Aware, Memory-Enabled & Cloned Voice</p>", unsafe_allow_html=True)

# Main Application Tabs
tab_chat, tab_memory, tab_persona = st.tabs(["💬 Chat with Twin", "🧠 Memory Vault", "⚙️ Persona Customizer"])

with tab_chat:
    # Layout Columns
    col_chat, col_explain = st.columns([3, 2])

    # Left Column: Chat Interaction
    with col_chat:
        st.markdown("<h3 style='color: #60a5fa;'>💬 Talk to Vasu's Replica</h3>", unsafe_allow_html=True)
        
        # Display Chat Log
        chat_container = st.container(height=450)
        with chat_container:
            for chat_msg in st.session_state.chat_history:
                role = chat_msg["role"]
                content = chat_msg["content"]
                
                if role == "user":
                    with st.chat_message("user", avatar="💬"):
                        st.write(content)
                else:
                    with st.chat_message("assistant", avatar="👤"):
                        st.write(content)
                        if "audio_path" in chat_msg and chat_msg["audio_path"]:
                            st.audio(chat_msg["audio_path"])

        # Chat Input Method: Voice or Text
        st.markdown("---")
        chat_input_type = st.radio("Choose Input Method", ["Text Message", "Voice Clip"], horizontal=True)

        if chat_input_type == "Text Message":
            user_message = st.chat_input("Ask Vasu about his projects, experience, or hobbies...")
            if user_message:
                # Append User Message to Chat Log
                st.session_state.chat_history.append({"role": "user", "content": user_message})
                st.rerun()

        else:
            # Voice Clip Uploader (simulates microphone recorder input)
            voice_file = st.file_uploader("Upload Voice Recording", type=["wav", "mp3", "m4a"])
            if voice_file is not None:
                if st.button("Send Audio Message", use_container_width=True):
                    with st.spinner("Transcribing audio voice message..."):
                        try:
                            # 1. Transcribe audio using Whisper endpoint
                            files = {"file": (voice_file.name, voice_file.getvalue(), voice_file.type)}
                            transcribe_res = httpx.post(f"{API_BASE_URL}/audio/transcribe", files=files, timeout=60.0)
                            
                            if transcribe_res.status_code == 200:
                                transcription_text = transcribe_res.json().get("text", "")
                                st.info(f"Speech Transcribed: \"{transcription_text}\"")
                                
                                # Append user message
                                st.session_state.chat_history.append({"role": "user", "content": transcription_text})
                                st.rerun()
                            else:
                                st.error("Audio transcription failed.")
                        except Exception as e:
                            st.error(f"Error communicating with backend: {str(e)}")

    # Logic to handle backend LLM chat call
    if len(st.session_state.chat_history) > 0 and st.session_state.chat_history[-1]["role"] == "user":
        latest_msg = st.session_state.chat_history[-1]["content"]
        
        with st.spinner("Generating Vasu's response..."):
            try:
                payload = {
                    "session_id": st.session_state.session_id,
                    "message": latest_msg,
                    "use_rag": use_rag,
                    "use_memory": use_memory
                }
                res = httpx.post(f"{API_BASE_URL}/chat", json=payload, timeout=60.0)
                
                if res.status_code == 200:
                    data = res.json()
                    bot_response = data.get("response", "")
                    explainability_data = data.get("explainability", {})
                    
                    audio_path_url = None
                    
                    # Check if voice cloning response is selected
                    if voice_response and bot_response:
                        with st.spinner("Cloning Vasu's voice response..."):
                            tts_res = httpx.post(
                                f"{API_BASE_URL}/audio/synthesize", 
                                data={"text": bot_response}, 
                                timeout=60.0
                            )
                            if tts_res.status_code == 200:
                                audio_url = tts_res.json().get("audio_url")
                                audio_path_url = f"{API_BASE_URL}{audio_url}"
                    
                    # Store chat message
                    st.session_state.chat_history.append({
                        "role": "assistant", 
                        "content": bot_response,
                        "audio_path": audio_path_url
                    })
                    
                    # Store explainability metrics
                    st.session_state.last_explainability = explainability_data
                    
                    st.rerun()
                else:
                    try:
                        error_detail = res.json().get('detail', 'Unknown error')
                    except Exception:
                        error_detail = res.text
                    st.error(f"Failed to generate response from API server (Error {res.status_code}): {error_detail}")
            except Exception as e:
                st.error(f"Could not connect to API server: {str(e)}")

    # Right Column: Explainability & Meta Dashboard
    with col_explain:
        st.markdown("<h3 style='color: #60a5fa;'>🔍 Explainability Trace</h3>", unsafe_allow_html=True)
        
        if st.session_state.last_explainability is None:
            st.info("Start a conversation to see the inner reasoning of the Digital Twin.")
        else:
            exp = st.session_state.last_explainability
            
            # Confidence Metric Card
            st.markdown(f"""
            <div class="card">
                <div class="metric-title">Response Confidence Score</div>
                <div class="metric-value">{exp.get('confidence_score', 'N/A')}</div>
            </div>
            """, unsafe_allow_html=True)

            # Reasoning Path
            st.markdown(f"""
            <div class="card">
                <div class="metric-title">Reasoning Path</div>
                <p style="color: #cbd5e1; font-size: 0.95rem; margin-top: 0.5rem;">{exp.get('reason_for_answer', 'N/A')}</p>
            </div>
            """, unsafe_allow_html=True)

            # Retrieved Documents
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("<div class='metric-title'>Retrieved Knowledge Base (RAG)</div>", unsafe_allow_html=True)
            sources = exp.get("sources_used", [])
            if not sources:
                st.markdown("<p style='color: #64748b; font-size: 0.9rem;'>No external document chunks retrieved.</p>", unsafe_allow_html=True)
            else:
                for s in sources:
                    st.markdown(f"""
                    <div style="margin-top: 0.5rem; padding-bottom: 0.5rem; border-bottom: 1px solid rgba(255,255,255,0.05);">
                        <span class="source-tag">{s['source_file']}</span>
                        <span style="color: #10b981; font-size: 0.8rem;">Similarity: {int(s['relevance_score'] * 100)}%</span>
                    </div>
                    """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

            # Retrieved SQLite memory facts
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("<div class='metric-title'>SQLite Factual Memories</div>", unsafe_allow_html=True)
            mems = exp.get("memories_used", [])
            if not mems:
                st.markdown("<p style='color: #64748b; font-size: 0.9rem;'>No long-term memories retrieved.</p>", unsafe_allow_html=True)
            else:
                for m in mems:
                    st.markdown(f"🧠 `{m}`")
            st.markdown("</div>", unsafe_allow_html=True)

            # Prompt summary
            st.markdown(f"""
            <div class="card">
                <div class="metric-title">Prompt Engine Metadata</div>
                <p style="color: #cbd5e1; font-size: 0.85rem; margin-top: 0.5rem; font-family: monospace;">{exp.get('prompt_summary', '')}</p>
            </div>
            """, unsafe_allow_html=True)

with tab_memory:
    st.markdown("<h3 style='color: #60a5fa;'>🧠 Memory Vault</h3>", unsafe_allow_html=True)
    st.write("Manage the long-term factual memories stored in the SQLite database.")
    
    # Left column for adding memory, right column for viewing and deleting
    col_add_mem, col_view_mem = st.columns([2, 3])
    
    with col_add_mem:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("Add Factual Memory")
        with st.form("add_memory_form", clear_on_submit=True):
            mem_key = st.text_input("Memory Key", placeholder="e.g. favourite_food, birthplace")
            mem_val = st.text_area("Memory Value", placeholder="e.g. Vasu loves eating paneer butter masala.")
            submit_mem = st.form_submit_button("Save Memory", use_container_width=True)
            
            if submit_mem:
                if not mem_key.strip() or not mem_val.strip():
                    st.error("Both Key and Value are required.")
                else:
                    try:
                        payload = {"key": mem_key, "value": mem_val}
                        r = httpx.post(f"{API_BASE_URL}/memory", json=payload)
                        if r.status_code == 200:
                            st.success(f"Added memory for '{mem_key}'!")
                            st.rerun()
                        else:
                            st.error(f"Failed to add memory: {r.text}")
                    except Exception as e:
                        st.error(f"Error: {e}")
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col_view_mem:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader("Current Long-Term Facts")
        
        # Load facts
        facts = []
        try:
            r = httpx.get(f"{API_BASE_URL}/memory")
            if r.status_code == 200:
                facts = r.json().get("facts", [])
            else:
                st.error("Failed to load memories from backend.")
        except Exception as e:
            st.error(f"Could not connect to backend: {e}")
            
        if not facts:
            st.info("No long-term memories stored yet.")
        else:
            # Display as a dataframe
            import pandas as pd
            df = pd.DataFrame(facts)
            df.columns = ["Memory Key", "Factual Description"]
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            st.markdown("---")
            st.subheader("Delete Memory")
            # Dropdown of keys to delete
            keys = [f["key"] for f in facts]
            key_to_delete = st.selectbox("Select Memory Key to Remove", keys)
            if st.button("Delete Selected Memory", type="primary", use_container_width=True):
                try:
                    r = httpx.delete(f"{API_BASE_URL}/memory/{key_to_delete}")
                    if r.status_code == 200:
                        st.success(f"Deleted memory for '{key_to_delete}'!")
                        st.rerun()
                    else:
                        st.error(f"Failed to delete memory: {r.text}")
                except Exception as e:
                    st.error(f"Error: {e}")
        st.markdown("</div>", unsafe_allow_html=True)

with tab_persona:
    st.markdown("<h3 style='color: #60a5fa;'>⚙️ Persona Customizer</h3>", unsafe_allow_html=True)
    st.write("Modify the digital twin's system persona, interests, and communication style at runtime.")
    
    # Switch/Create profile section
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    col_switch, col_create = st.columns([1, 1])
    
    active_profile = "vasu"
    profiles = ["vasu"]
    
    try:
        r_list = httpx.get(f"{API_BASE_URL}/persona/list")
        if r_list.status_code == 200:
            profiles = r_list.json().get("profiles", ["vasu"])
            active_profile = r_list.json().get("active", "vasu")
    except Exception as e:
        st.error(f"Failed to load profile list: {e}")
        
    with col_switch:
        st.subheader("Switch Active Profile")
        selected_profile = st.selectbox("Select Profile", profiles, index=profiles.index(active_profile) if active_profile in profiles else 0)
        if selected_profile != active_profile:
            if st.button("Apply Profile Switch", use_container_width=True):
                try:
                    r_switch = httpx.post(f"{API_BASE_URL}/persona/switch", json={"profile_name": selected_profile})
                    if r_switch.status_code == 200:
                        st.success(f"Switched active profile to '{selected_profile}'!")
                        st.rerun()
                    else:
                        st.error(f"Failed to switch: {r_switch.text}")
                except Exception as e:
                    st.error(f"Error: {e}")
                    
    with col_create:
        st.subheader("Create New Profile")
        new_profile_name = st.text_input("New Profile Name", placeholder="e.g. vasu_formal, vasu_interviewer")
        if st.button("Create & Switch to Profile", use_container_width=True):
            if not new_profile_name.strip():
                st.error("Profile name is required.")
            else:
                clean_new_name = new_profile_name.strip().lower().replace(" ", "_")
                try:
                    r_switch = httpx.post(f"{API_BASE_URL}/persona/switch", json={"profile_name": clean_new_name})
                    if r_switch.status_code == 200:
                        st.success(f"Created and switched to profile '{clean_new_name}'!")
                        st.rerun()
                    else:
                        st.error(f"Failed to create/switch: {r_switch.text}")
                except Exception as e:
                    st.error(f"Error: {e}")
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Load current persona details
    persona_data = {}
    try:
        r_persona = httpx.get(f"{API_BASE_URL}/persona")
        if r_persona.status_code == 200:
            persona_data = r_persona.json()
    except Exception as e:
        st.error(f"Failed to load active persona details: {e}")
        
    if persona_data:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.subheader(f"Edit Active Profile: '{active_profile}'")
        
        with st.form("edit_persona_form"):
            col_p1, col_p2 = st.columns([1, 1])
            
            with col_p1:
                p_name = st.text_input("Name", value=persona_data.get("name", "Vasu"))
                style = persona_data.get("communication_style", {})
                p_vocab = st.text_input("Vocabulary", value=style.get("vocabulary", ""))
                p_depth = st.text_input("Technical Depth", value=style.get("technical_depth", ""))
                p_humor = st.text_input("Humor Level", value=style.get("humor_level", ""))
                p_greeting = st.text_input("Greeting Style", value=style.get("greeting_style", ""))
                
            with col_p2:
                p_formality = st.text_input("Formality", value=style.get("formality", ""))
                p_length = st.text_input("Preferred Sentence Length", value=style.get("sentence_length", ""))
                p_interests = st.text_area("Interests (comma-separated)", value=", ".join(persona_data.get("interests", [])))
                p_values = st.text_area("Core Values (comma-separated)", value=", ".join(persona_data.get("values", [])))
            
            st.markdown("---")
            p_phrases_list = style.get("frequently_used_phrases", [])
            p_phrases = st.text_area("Frequently Used Phrases (One per line)", value="\n".join(p_phrases_list))
            
            save_persona = st.form_submit_button("Save & Update Persona", use_container_width=True)
            
            if save_persona:
                # Parse inputs
                updated_profile = {
                    "name": p_name.strip(),
                    "communication_style": {
                        "vocabulary": p_vocab.strip(),
                        "technical_depth": p_depth.strip(),
                        "humor_level": p_humor.strip(),
                        "greeting_style": p_greeting.strip(),
                        "formality": p_formality.strip(),
                        "sentence_length": p_length.strip(),
                        "frequently_used_phrases": [phrase.strip() for phrase in p_phrases.split("\n") if phrase.strip()]
                    },
                    "interests": [i.strip() for i in p_interests.split(",") if i.strip()],
                    "values": [v.strip() for v in p_values.split(",") if v.strip()]
                }
                
                try:
                    r_update = httpx.post(f"{API_BASE_URL}/persona", json=updated_profile)
                    if r_update.status_code == 200:
                        st.success(f"Successfully saved persona details for '{active_profile}'!")
                        st.rerun()
                    else:
                        st.error(f"Failed to save profile: {r_update.text}")
                except Exception as e:
                    st.error(f"Error: {e}")
        st.markdown("</div>", unsafe_allow_html=True)
