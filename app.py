import streamlit as st
from groq import Groq
import chromadb
import glob

st.set_page_config(page_title="Whisper", page_icon="🎀", layout="wide", initial_sidebar_state="collapsed")
st.title("Welcome to Whisper Circle")

client = Groq(api_key=st.secrets["GROQ_API_KEY"])
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
            chunks = [c.strip() for c in content.split("---") if c.strip()]
            for chunk in chunks:
                all_chunks.append(chunk)
                all_metadatas.append({"source": filepath})
                all_ids.append(f"doc_{chunk_id}")
                chunk_id += 1
        collection.upsert(documents=all_chunks, metadatas=all_metadatas, ids=all_ids)

    return collection

collection = get_collection()

def extract_content(stream):
    for chunk in stream:
        delta = chunk.choices[0].delta
        if delta.content:
            yield delta.content

if "groq_model" not in st.session_state:
    st.session_state["groq_model"] = "openai/gpt-oss-20b"
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask something..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    results = collection.query(query_texts=[prompt], n_results=3)
    context = "\n\n".join(results["documents"][0])

    system_prompt = f"""You are Whisper, a gentle, non-judgmental assistant answering questions about female health.
Answer ONLY using the context below. If the context doesn't cover the question, say so honestly and suggest they consult a healthcare provider — never guess.

Context:
{context}"""

    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model=st.session_state["groq_model"],
            messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
            stream=True,
        )
        response = st.write_stream(extract_content(stream))
    st.session_state.messages.append({"role": "assistant", "content": response})
 stream = client.chat.completions.create(
            model=st.session_state["groq_model"],
            messages=[{"role": "system", "content": system_prompt}] +
                     [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
            stream=True,
        )
