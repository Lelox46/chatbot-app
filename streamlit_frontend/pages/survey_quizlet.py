import streamlit as st

st.title("📝 Fragebogen: Quizlet")

st.markdown("""
Bitte fülle diesen Fragebogen aus:

👉 [Microsoft Forms Fragebogen zu Quizlet](https://forms.office.com/dein-link)

Wenn du fertig bist, geht’s weiter:
""")

if st.session_state.gruppe == "quizlet_zuerst":
    st.page_link("streamlit_frontend/pages/app2.py", label="Jetzt zum Chatbot")
else:
    st.page_link("streamlit_frontend/pages/conclusion.py", label="Zur Abschluss-Seite")
