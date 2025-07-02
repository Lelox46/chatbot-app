import streamlit as st

st.title("📝 Fragebogen: Chatbot")

st.markdown("""
Bitte fülle den Fragebogen aus:

👉 [Microsoft Forms Fragebogen zum Chatbot](https://forms.office.com/Pages/ResponsePage.aspx?id=oHqj8b2VxkW_mcmwY826GBQKxn3NUhFCm8LD9shjbppUN1ZLMkw1VUdUVUtIMzJOVzdTTjFHTVJJUC4u)

Wenn du fertig bist, geht’s weiter:
""")

if st.session_state.gruppe == "chatbot_zuerst":
    if st.button("➡️ Weiter zur Quizlet-Lektion"):
        st.switch_page("pages/quizlet.py")
else:
    if st.button("➡️ Zur Abschluss-Seite"):
        st.switch_page("pages/z_conclusion.py")
