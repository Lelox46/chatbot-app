import streamlit as st

st.title("📘 Quizlet-Lektion")

st.markdown("""
Bitte mache nun die folgende Lektion auf Quizlet:

👉 [Hier geht's zur Lektion](https://quizlet.com/de/karteikarten/bitcoin-1040731195?i=wyc9j&x=1jqt)

Wenn du fertig bist, klicke unten weiter.
""")

st.page_link("pages/survey_quizlet.py", label="Zum Fragebogen (Quizlet)")
