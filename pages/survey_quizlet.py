import streamlit as st

st.title("📝 Fragebogen: Quizlet")

st.markdown("""
Bitte fülle diesen Fragebogen aus:

👉 [Microsoft Forms Fragebogen zu Quizlet](https://forms.office.com/Pages/ResponsePage.aspx?id=oHqj8b2VxkW_mcmwY826GBQKxn3NUhFCm8LD9shjbppUOVA5NjNFQUJVMFo3QlFBVFJXUEIyMzJIVS4u)

Wenn du fertig bist, geht’s weiter:
""")

if st.session_state.gruppe == "quizlet_zuerst":
    if st.button("➡️ Jetzt zum Chatbot"):
        st.switch_page("pages/chatbot.py")
else:
    if st.button("Zur Abschluss-Seite"):
        st.switch_page("pages/conclusion.py")
