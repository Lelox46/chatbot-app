import streamlit as st
import random

st.set_page_config(page_title="Lernen mit KI - Evaluation")
st.title("🚀 Willkommen zur Evaluation!")

# Wenn noch keine Gruppe gespeichert ist, zeige Button:
if "gruppe" not in st.session_state:
    if st.button("🔁 Teilnahme starten"):
        st.session_state.gruppe = random.choice(["chatbot_zuerst", "quizlet_zuerst"])
        st.experimental_rerun()
    else:
        st.stop()  # ⛔️ Beende hier, um nichts vorzeitig zu zeigen

# Jetzt: nach Zufallswahl weiterleiten
if st.session_state.gruppe == "chatbot_zuerst":
    st.write("👉 Du beginnst mit dem **Chatbot**.")
    st.page_link("streamlit_frontend/pages/chatbot.py", label="Weiter zum Chatbot")

elif st.session_state.gruppe == "quizlet_zuerst":
    st.write("👉 Du beginnst mit der **Quizlet-Lektion**.")
    st.page_link("streamlit_frontend/pages/quizlet.py", label="Weiter zur Quizlet-Lektion")
