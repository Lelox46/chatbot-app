import streamlit as st

st.title("📝 Fragebogen: Chatbot")

st.markdown("""
Bitte fülle den Fragebogen aus:

👉 [Microsoft Forms Fragebogen zum Chatbot](https://forms.office.com/dein-link)

Wenn du fertig bist, geht’s weiter:
""")

if st.session_state.gruppe == "chatbot_zuerst":
    st.page_link("streamlit_frontend/pages/quizlet.py", label="Jetzt zur Quizlet-Lektion")
else:
    st.page_link("streamlit_frontend/pages/conclusion.py", label="Zur Abschluss-Seite")
