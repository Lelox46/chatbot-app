import streamlit as st
import random

st.set_page_config(page_title="Lernen mit KI - Evaluation")

st.title("🚀 Willkommen zur Evaluation!")

if "gruppe" not in st.session_state:
    st.session_state.gruppe = random.choice(["chatbot_zuerst", "quizlet_zuerst"])

if st.session_state.gruppe == "chatbot_zuerst":
    st.write("👉 Du beginnst mit dem **Chatbot**.")
    st.page_link("streamlit_frontend/app2.py", label="Weiter zum Chatbot")

elif st.session_state.gruppe == "quizlet_zuerst":
    st.write("👉 Du beginnst mit der **Quizlet-Lektion**.")
    st.page_link("streamlit_frontend/quizlet.py", label="Weiter zur Quizlet-Lektion")
