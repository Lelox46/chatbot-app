import streamlit as st
import os
import sys
import uuid
import time
import base64
from bitcoin_chatbot import build_chain, FRAGENKATALOG  # Dein umgewandelter Langflow-Flow

# ──────────────────────────────────────────────────────────────────────────
# Asset-Zugriff (für .exe-Kompatibilität optional)
# ──────────────────────────────────────────────────────────────────────────
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(__file__)

def get_asset_path(rel_path):
    return os.path.join(base_path, rel_path)

# ──────────────────────────────────────────────────────────────────────────
# Style: Hintergrundbilder & Chat CSS
# ──────────────────────────────────────────────────────────────────────────
def get_base64_image(path):
    with open(path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

def set_background(png_file):
    bg = get_base64_image(get_asset_path(png_file))
    st.markdown(f"""
        <style>
        [data-testid="stAppViewContainer"] {{
            background-image: url("data:image/png;base64,{bg}");
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        </style>
    """, unsafe_allow_html=True)

set_background("assets/bitcoin_bg.png")
bg2 = get_base64_image(get_asset_path("assets/bg.png"))
st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"] > .main {{
        background-image: url("data:image/png;base64,{bg2}");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    </style>
""", unsafe_allow_html=True)

# Chat-Bubble Styles
st.markdown("""
<style>
.chat-bubble {
    padding: 10px 15px;
    border-radius: 10px;
    margin: 10px 0;
    color: white;
    border: 4px solid #000;
    font-family: "Arial";
    background-color: #1c222b;
}
.bot { background-color: #1c222; text-align: left; }
.user { background-color: #1c222; text-align: right; }
.typing { background-color: #1c222; text-align: left; }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────
# UI Titel + Banner
# ──────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Bitcoin Chatbot")
st.markdown("<h1 style='text-align:center;'>Bitcoin Chatbot</h1>", unsafe_allow_html=True)
st.image(get_asset_path("assets/bitcoin_banner.jpg"), use_container_width=True)
st.markdown("<h3 style='text-align:center;'>Lerne alles über Bitcoin! Stell mir einfach eine Frage!</h3>", unsafe_allow_html=True)
st.markdown("---")

# ──────────────────────────────────────────────────────────────────────────
# Session-State Setup
# ──────────────────────────────────────────────────────────────────────────
for key in ["messages","user_just_sent","user_input_value",
            "bot_typing","pending_bot_response","awaiting_typing_display"]:
    if key not in st.session_state:
        st.session_state[key] = False if "typing" in key or "just_sent" in key or "pending" in key or "awaiting" in key else []

# Initialisiere die Chain einmal pro Session
if "chain" not in st.session_state:
    # ❗ Stelle sicher, dass diese Werte in .streamlit/secrets.toml gesetzt sind
    st.session_state.chain = build_chain(
        token=st.secrets["ASTRA_TOKEN"],
        api_endpoint=st.secrets["ASTRA_API_ENDPOINT"],
        database=st.secrets["ASTRA_DB"],
        collection=st.secrets["ASTRA_COLLECTION"]
    )

# ──────────────────────────────────────────────────────────────────────────
# Verlauf anzeigen
# ──────────────────────────────────────────────────────────────────────────
with st.container():
    for sender, message in st.session_state.messages:
        css = "bot" if sender == "Bot" else "user"
        st.markdown(
            f"<div class='chat-bubble {css}'><strong>{sender}:</strong><br>{message}</div>",
            unsafe_allow_html=True
        )
    if st.session_state.bot_typing and not st.session_state.pending_bot_response:
        st.markdown("<div class='chat-bubble typing'><strong>Thinking...</strong></div>", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────
# PHASE 1.5: Warte auf "Thinking..." Anzeige, dann rerun
# ──────────────────────────────────────────────────────────────────────────
if st.session_state.awaiting_typing_display:
    st.session_state.bot_typing = True
    st.session_state.awaiting_typing_display = False
    st.session_state.user_just_sent = True
    st.rerun()

# ──────────────────────────────────────────────────────────────────────────
# PHASE 2: Antwort generieren über LangChain
# ──────────────────────────────────────────────────────────────────────────
if st.session_state.user_just_sent:
    st.session_state.user_just_sent = False
    try:
        result = st.session_state.chain({
            "question": st.session_state.user_input_value,
            "fragenkatalog": FRAGENKATALOG
        })
        st.session_state.pending_bot_response = result["answer"]
    except Exception as e:
        st.session_state.messages.append(("Bot", f"Fehler: {e}"))
        st.session_state.bot_typing = False
    st.rerun()

# ──────────────────────────────────────────────────────────────────────────
# PHASE 3: "Typing" animieren und anzeigen
# ──────────────────────────────────────────────────────────────────────────
if st.session_state.pending_bot_response:
    st.session_state.bot_typing = False
    typed_resp = ""
    placeholder = st.empty()
    for ch in st.session_state.pending_bot_response:
        typed_resp += ch
        placeholder.markdown(f"<div class='chat-bubble typing'><strong>Bot:</strong><br>{typed_resp}</div>", unsafe_allow_html=True)
        time.sleep(0.015)
    st.session_state.messages.append(("Bot", st.session_state.pending_bot_response))
    st.session_state.pending_bot_response = None
    placeholder.empty()
    st.rerun()

# ──────────────────────────────────────────────────────────────────────────
# Eingabefeld
# ──────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
:root { --chat-h: 40px; }
div[data-testid="stForm"] {
  border: none !important;
  box-shadow: none !important;
  background: transparent !important;
  padding: 0 !important;
  margin: 0 !important;
}
div[data-testid="stTextInput"] > div {
  height: var(--chat-h) !important;
  max-height: var(--chat-h) !important;
  overflow: visible !important;
  padding: 0 !important;
  margin: 0 !important;
}
div[data-testid="stTextInput"] input {
  width: 100% !important;
  height: var(--chat-h) !important;
  line-height: var(--chat-h) !important;
  box-sizing: border-box !important;
  padding: 0 0.75rem !important;
  margin: 0 !important;
  border: 4px solid #000 !important;
  border-radius: 10px !important;
  background-color: #1c222b !important;
  color: white !important;
}
div[data-testid="stColumns"] > div:nth-child(2) {
  display: flex !important;
  align-items: center !important;
  padding: 0 !important;
  margin: 0 !important;
}
div[data-testid="stButton"] > button {
  width: var(--chat-h) !important;
  height: var(--chat-h) !important;
  padding: 0 !important;
  min-width: unset !important;
  border: none !important;
  box-shadow: none !important;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
""", unsafe_allow_html=True)

with st.form(key="chat_form", clear_on_submit=True):
    col1, col2 = st.columns([0.93, 0.07])
    with col1:
        user_input = st.text_input("", key="input_box", placeholder="Frag mich was über Bitcoin…", label_visibility="collapsed")
    with col2:
        send = st.form_submit_button("➤")

    if send and user_input:
        st.session_state.messages.append(("User", user_input))
        st.session_state.user_input_value = user_input
        st.session_state.awaiting_typing_display = True
        st.rerun()
