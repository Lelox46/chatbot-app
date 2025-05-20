import streamlit as st
import sys, os
import uuid
from dotenv import load_dotenv
from langflow.load import run_flow_from_json
import time
import base64

# === Schritt 1: Sicherer Asset-Zugriff für .exe ===
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(__file__)

def get_asset_path(rel_path):
    return os.path.join(base_path, rel_path)

# === ===

load_dotenv()

TWEAKS = {
    "ChatInput-6Eftk": {}, "ParseData-dG9Hf": {}, "Prompt-GZMeu": {},
    "SplitText-d6dCS": {}, "ChatOutput-6cPPz": {}, "AstraDB-gN9Qf": {},
    "AstraDB-kam8Q": {}, "OllamaModel-sLFkE": {}, "OllamaEmbeddings-nwFwb": {},
    "OllamaEmbeddings-Z2oCq": {}, "AstraDBChatMemory-5wMF2": {},
    "Memory-exuRZ": {}, "StoreMessage-mnHis": {}, "AstraDB-3K50i": {},
    "ParseData-CnnEM": {}, "OllamaEmbeddings-KGDSK": {}, "OpenAIModel-FzVzM": {},
    "File-BInQn": {}
}

# Generate a unique user ID
user_id = str(uuid.uuid4())
FLOW_PATH = get_asset_path("langflow_rag_openai_cloud.json")

st.set_page_config(page_title="Bitcoin Chatbot")

# Helpers for background images
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

# Call background images
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

# Chat bubble styling
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

st.markdown("<h1 style='text-align:center;'>Bitcoin Chatbot</h1>", unsafe_allow_html=True)
st.image(get_asset_path("assets/bitcoin_banner.jpg"), use_container_width=True)
st.markdown("<h3 style='text-align:center;'>Lerne alles über Bitcoin! Stell mir einfach eine Frage!</h3>", unsafe_allow_html=True)
st.markdown("---")

# Session state setup
for key in ["messages","user_just_sent","user_input_value",
            "bot_typing","pending_bot_response","awaiting_typing_display"]:
    if key not in st.session_state:
        st.session_state[key] = False if "typing" in key or "just_sent" in key or "pending" in key or "awaiting" in key else []

# Display chat history
with st.container():
    for sender, message in st.session_state.messages:
        css = "bot" if sender == "Bot" else "user"
        st.markdown(
            f"<div class='chat-bubble {css}'><strong>{sender}:</strong><br>{message}</div>",
            unsafe_allow_html=True
        )
    if st.session_state.bot_typing and not st.session_state.pending_bot_response:
        st.markdown("<div class='chat-bubble typing'><strong>Thinking...</strong></div>", unsafe_allow_html=True)

# Phase 1.5: show "Thinking..." then rerun
if st.session_state.awaiting_typing_display:
    st.session_state.bot_typing = True
    st.session_state.awaiting_typing_display = False
    st.session_state.user_just_sent = True
    st.rerun()

# Phase 2: generate response
if st.session_state.user_just_sent:
    st.session_state.user_just_sent = False
    try:
        result = run_flow_from_json(
            flow=FLOW_PATH,
            input_value=st.session_state.user_input_value,
            session_id="streamlit-user-session",
            fallback_to_env_vars=True,
            tweaks=TWEAKS
        )
        st.session_state.pending_bot_response = result[0].outputs[0].outputs["message"]["message"]
    except Exception as e:
        st.session_state.messages.append(("Bot", f"Error: {e}"))
        st.session_state.bot_typing = False
    st.rerun()

# Phase 3: animate bot response
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

# Input CSS
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

# Input-Feld mit Submit-Button
with st.form(key="chat_form", clear_on_submit=True):
    col1, col2 = st.columns([0.93, 0.07])
    with col1:
        user_input = st.text_input(
            label="", key="input_box",
            placeholder="Ask me something…",
            label_visibility="collapsed"
        )
    with col2:
        send = st.form_submit_button("➤")

    if send and user_input:
        st.session_state.messages.append(("User", user_input))
        st.session_state.user_input_value = user_input
        st.session_state.awaiting_typing_display = True
        st.rerun()
