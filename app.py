import streamlit as st
import random

st.set_page_config(page_title="Lernen mit KI - Evaluation")
st.title("🚀 Willkommen zur Evaluation!")
st.write("Vielen Dank, dass du dir kurz Zeit nimmst. Meine Bachelorarbeit beschäftigt sich mit KI als Lernmethode. In dieser Evaluation hast du die Möglichkeit einen KI-Chatbot und eine gewöhnliche Lernapp auszuprobieren und zu vergleichen. Diese Umfrage ist optimiert für PC´s, funktioniert aber auch auf dem Smartphone.")
st.write("Bitte klick unten auf den Button um loszulegen.")

# Wenn noch keine Gruppe gespeichert ist, zeige Button:
if "gruppe" not in st.session_state:
    if st.button("🔁 Teilnahme starten"):
        st.session_state.gruppe = random.choice(["chatbot_zuerst", "quizlet_zuerst"])
        st.rerun()
    else:
        st.stop()  # ⛔️ Beende hier, um nichts vorzeitig zu zeigen

# Jetzt: nach Zufallswahl weiterleiten
if st.session_state.gruppe == "chatbot_zuerst":
    st.write("Beginnen wir mit dem Chatbot. Klick unten auf den Button um den Chatbot zu öffnen. Du kannst ihn für ein paar minuten testen und dann dein Feedback geben.😀")
    st.page_link("pages/chatbot.py", label="Weiter zum Chatbot")

elif st.session_state.gruppe == "quizlet_zuerst":
    st.write("Beginnen wir mit einer Quizlet Lektion. Klick auf den Button unten um loszulegen. Du kannst anschließend kurz Feedback geben und dann gehts weiter mit dem Chatbot. 😀")
    st.page_link("pages/quizlet.py", label="Weiter zur Quizlet-Lektion")
