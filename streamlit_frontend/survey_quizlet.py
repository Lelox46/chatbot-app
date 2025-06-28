import streamlit as st

st.title("📝 Fragebogen: Quizlet")

st.markdown("""
Bitte fülle diesen Fragebogen aus:

👉 [Microsoft Forms Fragebogen zu Quizlet](https://forms.office.com/dein-link)

Wenn du fertig bist, geht’s weiter:
""")

if st.session_state.gruppe == "quizlet_zuerst":
    st.page_link("pages/1_Chatbot.py", label="Jetzt zum Chatbot")
else:
    st.page_link("pages/5_Abschluss.py", label="Zur Abschluss-Seite")
