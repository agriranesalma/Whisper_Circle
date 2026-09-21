import streamlit as st
from groq import Groq
import chromadb
import glob
import os
import re

st.set_page_config(
    page_title="Whisper Circle",
    page_icon="🎀",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ---------- STYLING ----------
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Caveat:wght@600;700&family=Fredoka:wght@600;700&family=Nunito:wght@400;600;700&family=Plus+Jakarta+Sans:wght@600;700&display=swap');

    /* Keyframe Animations */
    @keyframes floatAnimation {
        0% { transform: translateY(0px) rotate(0deg); }
        50% { transform: translateY(-7px) rotate(2deg); }
        100% { transform: translateY(0px) rotate(0deg); }
    }

    @keyframes pulseGlow {
        0% { box-shadow: 0 0 20px rgba(232, 116, 154, 0.35); }
        50% { box-shadow: 0 0 38px rgba(201, 82, 122, 0.6); }
        100% { box-shadow: 0 0 20px rgba(232, 116, 154, 0.35); }
    }

    @keyframes gradientShimmer {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* Ambient Background Hue */
    html, body, .stApp {
        background: 
            radial-gradient(circle at 15% 10%, rgba(248, 190, 212, 0.65) 0%, transparent 45%),
            radial-gradient(circle at 85% 20%, rgba(232, 116, 154, 0.30) 0%, transparent 50%),
            radial-gradient(circle at 50% 95%, rgba(247, 212, 180, 0.25) 0%, transparent 50%),
            #FFF5F8 !important;
    }

    [data-testid="stHeader"] {
        background: transparent !important;
        box-shadow: none !important;
    }

    /* Glassmorphism Hero Card */
    .whisper-hero-card {
        background: rgba(255, 255, 255, 0.78);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1.5px solid rgba(245, 198, 214, 0.7);
        border-radius: 26px;
        padding: 20px 20px 16px 20px;
        text-align: center;
        margin: 0 auto 20px auto;
        max-width: 680px;
        box-shadow: 0 12px 30px rgba(201, 82, 122, 0.08), inset 0 0 20px rgba(255, 255, 255, 0.9);
    }

    /* SDG Hackathon Pill Badge */
    .whisper-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: linear-gradient(135deg, #FFE8F0, #FAD0DD);
        border: 1px solid #F3B6C8;
        color: #B8325E;
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-weight: 700;
        font-size: 10px;
        letter-spacing: 1px;
        text-transform: uppercase;
        padding: 3px 12px;
        border-radius: 16px;
        margin-bottom: 8px;
        box-shadow: 0 2px 8px rgba(201, 82, 122, 0.10);
    }

    /* Floating Logo Container */
    .whisper-logo-wrapper {
        display: inline-block;
        position: relative;
        animation: floatAnimation 4s ease-in-out infinite;
        margin-bottom: 2px;
    }

    .whisper-logo {
        width: 68px;
        height: 68px;
        border-radius: 50%;
        background: linear-gradient(135deg, #FFE3EC 0%, #F3A8BD 50%, #E8749A 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 34px;
        border: 2.5px solid #FFFFFF;
        animation: pulseGlow 3s infinite;
    }

    /* Multi-Tone Title */
    .whisper-title {
        font-family: 'Fredoka', sans-serif !important;
        font-weight: 700 !important;
        font-size: 3.2rem !important;
        line-height: 1.1 !important;
        margin: 2px 0 2px 0 !important;
        letter-spacing: -1px;
        background: linear-gradient(120deg, #A8244E 0%, #E85D88 35%, #C9527A 70%, #8C1C3E 100%);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: gradientShimmer 5s ease infinite;
        filter: drop-shadow(0 3px 8px rgba(201, 82, 122, 0.12));
    }

    /* Tagline Quote */
    .whisper-tagline {
        font-family: 'Caveat', cursive !important;
        color: #8C3B5C !important;
        font-weight: 700 !important;
        font-size: 26px !important;
        line-height: 1.2 !important;
        margin: 4px auto 10px auto !important;
        max-width: 540px;
        letter-spacing: 0.2px;
    }

    /* Divider with Center Accent */
    .whisper-divider-custom {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
        margin-top: 6px;
    }

    .whisper-divider-line {
        height: 2px;
        width: 50px;
        background: linear-gradient(90deg, transparent, #E8749A, transparent);
        border-radius: 2px;
    }

    .whisper-divider-icon {
        font-size: 12px;
        color: #E8749A;
    }

    /* Chat Messages Styling */
    [data-testid="stChatMessage"] {
        background-color: #FFFFFF !important;
        border: 1px solid #F7DCE6 !important;
        border-radius: 22px !important;
        padding: 16px 20px !important;
        margin-bottom: 14px !important;
        box-shadow: 0 4px 15px rgba(201, 82, 122, 0.05) !important;
    }

    [data-testid="stChatMessage"] p, 
    [data-testid="stChatMessage"] li, 
    [data-testid="stChatMessage"] span, 
    [data-testid="stChatMessage"] div {
        color: #5A3547 !important;
        font-size: 16px !important;
    }

    [data-testid="stChatMessageAvatarUser"] {
        background: linear-gradient(135deg, #F3B6C8, #E8749A) !important;
    }

    [data-testid="stChatMessageAvatarAssistant"] {
        background: linear-gradient(135deg, #FFFFFF, #FBE4EC) !important;
        border: 1.5px solid #F5C6D6 !important;
    }

    /* Chat Input Bar */
    [data-testid="stChatInput"] {
        border-radius: 28px !important;
        border: 2px solid #F3C3D5 !important;
        box-shadow: 0 6px 20px rgba(201, 82, 122, 0.12) !important;
        background-color: #FFFFFF !important;
    }

    [data-testid="stChatInput"] textarea {
        color: #5A3547 !important;
        font-size: 15px !important;
    }

    [data-testid="stChatInput"] textarea::placeholder {
        color: #C28299 !important;
    }

    [data-testid="stExpander"] {
        border: 1px solid #F5C6D6 !important;
        border-radius: 16px !important;
        background-color: #FFFBFC !important;
    }

    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-thumb { background: #F3C3D5; border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

# ---------- HEADER ----------
st.markdown("""
    <div class="whisper-hero-card">
        <div class="whisper-badge">
            ✨ UN SDG 3 & 5 • Female Health Space ✨
        </div>
        <br>
        <div class="whisper-logo-wrapper">
            <div class="whisper-logo">🎀</div>
        </div>
        <h1 class="whisper-title">Whisper Circle</h1>
        <p class="whisper-tagline">“a gentle space for the questions you've never asked out loud”</p>
        <div class="whisper-divider-custom">
            <div class="whisper-divider-line"></div>
            <div class="whisper-divider-icon">🌸</div>
            <div class="whisper-divider-line"></div>
        </div>
    </div>
""", unsafe_allow_html=True)

# ---------- GROQ CLIENT ----------
client = Groq(api_key=st.secrets["GROQ_API_KEY"])


def extract_content(stream):
    for chunk in stream:
        delta = chunk.choices[0].delta
        if delta.content:
            yield delta.content


# ---------- BUILD / LOAD RAG KNOWLEDGE BASE ----------
@st.cache_resource
def get_collection():
    chroma_client = chromadb.PersistentClient(path="./my_chromadb_data")
    collection = chroma_client.get_or_create_collection(name="girls_questions")

    if collection.count() == 0:
        all_chunks, all_metadatas, all_ids = [], [], []
        chunk_id = 0
        for filepath in glob.glob("data/*.md"):
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Split the file by the "---" separator
            chunks = [c.strip() for c in content.split("---") if c.strip()]
            
            for chunk in chunks:
                all_chunks.append(chunk)
                
                # Search for the source link in the chunk
                url_match = re.search(r'Source:\s*(https?://[^\s]+)', chunk)
                if url_match:
                    actual_source = url_match.group(1)
                else:
                    actual_source = os.path.basename(filepath) # Fallback if no link is found
                
                all_metadatas.append({"source": actual_source})
                all_ids.append(f"doc_{chunk_id}")
                chunk_id += 1
                
        if all_chunks:
            collection.upsert(documents=all_chunks, metadatas=all_metadatas, ids=all_ids)

    return collection


collection = get_collection()

# ---------- SESSION STATE ----------
if "groq_model" not in st.session_state:
    st.session_state["groq_model"] = "openai/gpt-oss-20b"
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------- DISPLAY CHAT HISTORY ----------
for message in st.session_state.messages:
    avatar = "💌" if message["role"] == "user" else "🌸"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# ---------- HANDLE NEW INPUT ----------
if prompt := st.chat_input("Ask something, freely..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="💌"):
        st.markdown(prompt)

    # Retrieval step
    results = collection.query(query_texts=[prompt], n_results=3)
    retrieved_chunks = results["documents"][0]
    retrieved_sources = [m["source"] for m in results["metadatas"][0]]
    context = "\n\n".join(retrieved_chunks)

    system_prompt = f"""You are Whisper, a gentle, non-judgmental assistant answering questions about female health and wellbeing.
Answer warmly and clearly, ONLY using the context below. If the context doesn't cover the question, say so honestly and suggest they consult a healthcare provider — never guess.

Context:
{context}"""

    with st.chat_message("assistant", avatar="🌸"):
        stream = client.chat.completions.create(
            model=st.session_state["groq_model"],
            messages=[{"role": "system", "content": system_prompt}] +
                     [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
            stream=True,
        )
        response = st.write_stream(extract_content(stream))

        unique_sources = sorted(set(retrieved_sources))
        with st.expander("🩷 Sources"):
            for src in unique_sources:
                st.caption(src)

    st.session_state.messages.append({"role": "assistant", "content": response})
