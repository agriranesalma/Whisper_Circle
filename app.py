import streamlit as st
st.title("Welcome to Whisper Circle")
st.set_page_config(page_title="Whisper Circle", page_icon="🎀", layout="centered")
question = st.text_area("Ask Your Question Freely", height= 100)

with st.chat_message("user"):
st.write("How long is a normal cycle?")
with st.chat_message("assistant"):
st.write("Typically around 28 days, though it varies person to person.")
prompt = st.chat_input("Ask something...")
if prompt:
st.write(f"You asked: {prompt}")
