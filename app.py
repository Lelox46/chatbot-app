import time
import base64
from pathlib import Path

import streamlit as st

# Falls du die neue OpenAI-API nutzt:
try:
    from openai import OpenAI
    _has_new_openai = True
except Exception:
    _has_new_openai = False
import openai  # bleibt als Fallback importiert


# ────────────────────────────────────────────────
# Page config MUSS vor jeder Ausgabe stehen
# ────────────────────────────────────────────────
st.set_page_config(
    page_title="Quester AI",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ────────────────────────────────────────────────
# Streamlit UI-Elemente ausblenden (oben/unten/rechts)
# ────────────────────────────────────────────────
st.markdown("""
<style>
/* Menü oben rechts (Hamburger, inkl. GitHub-Link) */
#MainMenu {visibility: hidden;}

/* Standard-Header-Leiste komplett ausblenden */
div[data-testid="stHeader"] {display: none;}

/* Footer unten links */
footer {visibility: hidden;}

/* Toolbar / Status-Widgets / User-Badge unten rechts */
[data-testid="stStatusWidget"] {visibility: hidden;}
[data-testid="stToolbar"] {visibility: hidden;}

/* Optional: Sidebar komplett ausblenden (inkl. Collapser) */
section[data-testid="stSidebar"] {display: none;}
div[data-testid="stSidebarNav"] {display: none;}
</style>
""", unsafe_allow_html=True)


# ────────────────────────────────────────────────
# OpenAI-API-Key + Client
# ────────────────────────────────────────────────
# Aus st.secrets laden (benenne bei dir ggf. korrekt)
api_key = st.secrets.get("OPENAI_API_KEY") or st.secrets.get("OPENAI_OPENAI_API_KEY")
if not api_key:
    st.stop()

if _has_new_openai:
    try:
        client = OpenAI(api_key=api_key)
    except Exception:
        client = None
else:
    client = None
openai.api_key = api_key  # Fallback für ältere Pakete


# ────────────────────────────────────────────────
# System-Prompt
# ────────────────────────────────────────────────
SYSTEM_PROMPT = """
Du bist ein hilfreicher Chatbot, der Fragen zu jedem Lernthema einfach, verständlich und sachlich korrekt beantwortet.
Schlage ein Lernthema vor, wenn der User kein eigenes vorgibt und nenne ein paar mögliche Lernthemen.
Vermeide Fachjargon und erkläre Begriffe wenn nötig. Halte dich so kurz wie möglich.
Stelle am Ende eine weiterführende Frage zum gleichen Thema. Bleibe immer beim aktuellen Thema.
""".strip()


# ────────────────────────────────────────────────
# Assets finden (robust, egal ob Datei im Root oder in /pages liegt)
# ────────────────────────────────────────────────
THIS_FILE = Path(__file__).resolve()

def find_assets_dir(start: Path, max_up: int = 4) -> Path:
    """Gehe nach oben, bis 'assets' gefunden wird (max_up Ebenen)."""
    p = start
    for _ in range(max_up + 1):
        cand = p / "assets"
        if cand.exists() and cand.is_dir():
            return cand
        p = p.parent
    raise FileNotFoundError("Konnte keinen 'assets' Ordner finden. Erwartet: <projekt>/assets/...")

ASSET_DIR = find_assets_dir(THIS_FILE.parent)

def get_asset_path(filename: str) -> str:
    p = (ASSET_DIR / filename).resolve()
    if not p.exists():
        raise FileNotFoundError(f"Asset nicht gefunden: {p}")
    return str(p)

def get_base64_image(path: str) -> str:
    with open(path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

def set_background(png_filename: str):
    try:
        bg64 = get_base64_image(get_asset_path(png_filename))
        st.markdown(f"""
            <style>
            [data-testid="stAppViewContainer"] {{
                background-image: url("data:image/png;base64,{bg64}");
                background-size: cover;
                background-repeat: no-repeat;
                background-attachment: fixed;
            }}
            </style>
        """, unsafe_allow_html=True)
    except FileNotFoundError as e:
        st.warning(str(e))


# ────────────────────────────────────────────────
# Hintergründe / Branding
# ────────────────────────────────────────────────
set_background("quester_background.png")

try:
    bg2 = get_base64_image(get_asset_path("Logo_text.png"))
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
except FileNotFoundError as e:
    st.warning(str(e))


# ────────────────────────────────────────────────
# Chat-Style
# ────────────────────────────────────────────────
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
.bot    { background-color: #1c222b; text-align: left; }
.user   { background-color: #1c222b; text-align: right; }
.typing { background-color: #1c222b; text-align: left; }

/* Input-/Button-Styles */
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
div.stButton > button.fragebogen {
    padding: 0.75em 1.5em;
    font-size: 1.1em;
    font-weight: bold;
    border-radius: 8px;
    border: 2px solid #fff;
    background-color: #1c222b;
    color: white;
    cursor: pointer;
    display: inline-block;
}
</style>
""", unsafe_allow_html=True)


# ────────────────────────────────────────────────
# Header / Branding
# ────────────────────────────────────────────────
try:
    st.image(get_asset_path("Logo_text.png"), use_container_width=True)
except FileNotFoundError as e:
    st.warning(str(e))

st.markdown("<h3 style='text-align:center;'>Dein persönlicher Lerncoach! Was willst du wissen?</h3>", unsafe_allow_html=True)
st.markdown("---")


# ────────────────────────────────────────────────
# Session-State Setup
# ────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
for key in ["user_just_sent", "user_input_value", "bot_typing", "pending_bot_response", "awaiting_typing_display"]:
    if key not in st.session_state:
        st.session_state[key] = False


# ────────────────────────────────────────────────
# Verlauf anzeigen
# ────────────────────────────────────────────────
with st.container():
    for msg in st.session_state.messages[1:]:
        sender = "Quester" if msg["role"] == "assistant" else "User"
        css = "bot" if sender == "Quester" else "user"
        st.markdown(
            f"<div class='chat-bubble {css}'><strong>{sender}:</strong><br>{msg['content']}</div>",
            unsafe_allow_html=True
        )
    if st.session_state.bot_typing and not st.session_state.pending_bot_response:
        st.markdown("<div class='chat-bubble typing'><strong>Quester:</strong><br>Thinking…</div>", unsafe_allow_html=True)


# ────────────────────────────────────────────────
# PHASE 1.5: "Thinking..." sichtbar machen
# ────────────────────────────────────────────────
if st.session_state.awaiting_typing_display:
    st.session_state.bot_typing = True
    st.session_state.awaiting_typing_display = False
    st.session_state.user_just_sent = True
    st.rerun()


# ────────────────────────────────────────────────
# PHASE 2: Antwort generieren
# ────────────────────────────────────────────────
def _call_openai(messages):
    # Neuer Client?
    if client is not None and hasattr(client, "chat") and hasattr(client.chat, "completions"):
        resp = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        return resp.choices[0].message.content

    # Legacy-Fallback
    resp = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    return resp["choices"][0]["message"]["content"]

if st.session_state.user_just_sent:
    st.session_state.user_just_sent = False
    try:
        st.session_state.pending_bot_response = _call_openai(st.session_state.messages)
    except Exception as e:
        st.session_state.messages.append({"role": "assistant", "content": f"Fehler bei der API-Abfrage: {e}"})
        st.session_state.bot_typing = False
    st.rerun()


# ────────────────────────────────────────────────
# PHASE 3: "Typing"-Animation und Ausgabe
# ────────────────────────────────────────────────
if st.session_state.pending_bot_response:
    st.session_state.bot_typing = False
    typed_resp = ""
    placeholder = st.empty()
    for ch in st.session_state.pending_bot_response:
        typed_resp += ch
        placeholder.markdown(f"<div class='chat-bubble typing'><strong>Quester:</strong><br>{typed_resp}</div>", unsafe_allow_html=True)
        time.sleep(0.015)
    st.session_state.messages.append({"role": "assistant", "content": st.session_state.pending_bot_response})
    st.session_state.pending_bot_response = None
    placeholder.empty()
    st.rerun()


# ────────────────────────────────────────────────
# Eingabefeld
# ────────────────────────────────────────────────
with st.form(key="chat_form", clear_on_submit=True):
    col1, col2 = st.columns([0.93, 0.07])
    with col1:
        user_input = st.text_input("", key="input_box", placeholder="Was willst du lernen?", label_visibility="collapsed")
    with col2:
        send = st.form_submit_button("➤")

    if send and user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.user_input_value = user_input
        st.session_state.awaiting_typing_display = True
        st.rerun()
