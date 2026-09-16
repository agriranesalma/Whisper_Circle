import streamlit as st
from openai import OpenAI

st.title("Welcome to Whisper Circle")
st.set_page_config(page_title="Whisper",page_icon="🎀",layout="wide", initial_sidebar_state="collapsed")

client= OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
if "openai_model" not in st.session_state:
  st.session_state["openai_model"]= "gpt-3.5-turbo"

if "messages" not in st.session_state:
  st.session_state.messages=[]
for message in st.session_state.messages:
  with st.chat_message(message["role"]):
    st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
