import streamlit as st

st.title("📘 Quizlet-Lektion")

st.markdown("""
Bitte mache nun die folgende Lektion auf Quizlet:

Lerne mit den Karteikärtchen solange bis du ein gutes Gefühl für die Lernmethode hast. Keine Sorge, du musst dir nicht alles merken 😄.

👉 [Hier geht's zur Lektion](https://quizlet.com/de/karteikarten/bitcoin-1040731195?i=wyc9j&x=1jqt)

Wenn du genug hast, klicke bitte unten weiter.
""")

st.page_link("pages/survey_quizlet.py", label="Zum Fragebogen (Quizlet)")
