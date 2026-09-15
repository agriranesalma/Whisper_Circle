import streamlit as st
st.title("Welcome to Whisper Circle")
st.set_page_config(page_title="Whisper",page_icon="🎀",layout="wide", initial_sidebar_state="collapsed")


prompt= st.chat_input("You are welcome to ask any question, this is a safe space")
if prompt:
  st.write(f"User has sent the following prompt:{prompt}")
