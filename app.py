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
    @import url('https://fonts.googleapis.com/css2?family=Caveat:wght@500;600&family=Fredoka:wght@500;600;700&family=Nunito:wght@400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Nunito', sans-serif;
    }

    /* Force background colors */
    .stApp {
        background: 
            radial-gradient(circle at 12% 8%, rgba(245, 198, 214, 0.55) 0%, transparent 40%),
            radial-gradient(circle at 90% 15%, rgba(232, 116, 154, 0.18) 0%, transparent 45%),
            radial-gradient(circle at 50% 100%, rgba(217, 168, 87, 0.10) 0%, transparent 50%),
            #FFF8FA !important;
    }

    [data-testid="stHeader"] {
        box-shadow: none !important;
        border-bottom: none !important;
        background: transparent !important;
    }

    /* Amplified Logo + Title */
    .whisper-header {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 18px;
        margin-top: 10px;
    }

    .whisper-logo {
        width: 80px;
        height: 80px;
        border-radius: 50%;
        background: linear-gradient(135deg, #FBE4EC, #F3B6C8);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 42px;
        box-shadow: 0 4px 15px rgba(201, 82, 122, 0.25);
        flex-shrink: 0;
    }

    .whisper-header h1 {
        font-family: 'Fredoka', sans-serif !important;
        font-weight: 700 !important;
        font-size: 3.5rem !important;
        color: #C9527A !important;
        margin: 0 !important;
        letter-spacing: -1px;
    }

    .whisper-tagline {
        text-align: center;
        font-family: 'Caveat', cursive !important;
        color: #A9738A;
        font-weight: 600;
        font-size: 36px; /* Increased for better visibility */
        margin-top: -5px;
        margin-bottom: 22px;
    }

    .whisper-divider {
        height: 4px;
        width: 80px;
        margin: 0 auto 30px auto;
        background: linear-gradient(90deg, #F0AFC4, #E8749A, #F0AFC4);
        border-radius: 4px;
    }

    /* Chat bubbles */
    [data-testid="stChatMessage"] {
        background-color: #FFFFFF;
        border: 1px solid #F7DCE6;
        border-radius: 20px;
        padding: 14px 18px;
        margin-bottom: 14px;
        box-shadow: 0 3px 10px rgba(201, 82, 122, 0.06);
    }

    [data-testid="stChatMessage"] p, 
    [data-testid="stChatMessage"] li, 
    [data-testid="stChatMessage"] span, 
    [data-testid="stChatMessage"] div {
        color: #5A3547 !important;
    }

    [data-testid="stChatMessageAvatarUser"] {
        background: linear-gradient(135deg, #F3B6C8, #E8749A) !important;
    }

    [data-testid="stChatMessageAvatarAssistant"] {
        background: linear-gradient(135deg, #FFFFFF, #FBE4EC) !important;
        border: 1px solid #F5C6D6 !important;
    }

    /* Clean Chat Input */
    [data-testid="stChatInput"] {
        border-radius: 26px !important;
        border: 2px solid #F3C3D5 !important;
        box-shadow: 0 4px 14px rgba(201, 82, 122, 0.10) !important;
        background-color: #FFFFFF !important;
    }

    [data-testid="stChatInput"] textarea {
        color: #5A3547 !important;
        background-color: transparent !important;
    }

    [data-testid="stChatInput"] textarea::placeholder {
        color: #D9A0B4 !important;
    }

    /* Source citation badge */
    .source-badge {
        display: inline-block;
        margin-top: 10px;
        font-size: 12px;
        color: #C9527A;
        background: #FDF0F5;
        border: 1px solid #F5C6D6;
        padding: 4px 12px;
        border-radius: 12px;
        font-weight: 700;
    }

    /* Expander */
    [data-testid="stExpander"] {
        border: 1px solid #F5C6D6 !important;
        border-radius: 14px !important;
        background-color: #FFFBFC !important;
    }

    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-thumb { background: #F3C3D5; border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

# ---------- HEADER ----------
st.markdown("""
    <div class="whisper-header">
        <div class="whisper-logo">🎀</div>
        <h1>Whisper Circle</h1>
    </div>
""", unsafe_allow_html=True)
st.markdown("<p class='whisper-tagline'>a gentle space for the questions you've never asked out loud</p>", unsafe_allow_html=True)
st.markdown("<div class='whisper-divider'></div>", unsafe_allow_html=True)

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
