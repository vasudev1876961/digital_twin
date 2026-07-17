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
