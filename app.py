import json
import smtplib
import tomllib
from email.mime.text import MIMEText
from pathlib import Path

import streamlit as st
from google import genai
from google.genai import types

from prompts import SUMMARY_REQUEST_PROMPT, SYSTEM_PROMPT, WELCOME_MESSAGE_TEMPLATE

MODEL_NAME = "gemini-2.5-flash"

st.set_page_config(page_title="ReceiptSnap", page_icon="🧾")


def load_app_secrets():
    local_secrets_file = Path(__file__).resolve().parent / "streamlit" / "secrets.toml"
    if local_secrets_file.exists():
        with local_secrets_file.open("rb") as secret_file:
            return tomllib.load(secret_file)

    try:
        return dict(st.secrets)
    except Exception:
        return {}


APP_SECRETS = load_app_secrets()
GEMINI_API_KEY = APP_SECRETS.get("GEMINI_API_KEY", "")
GMAIL_ADDRESS = APP_SECRETS.get("GMAIL_ADDRESS", "")
GMAIL_APP_PASSWORD = APP_SECRETS.get("GMAIL_APP_PASSWORD", "")

if not (GEMINI_API_KEY and GMAIL_ADDRESS and GMAIL_APP_PASSWORD):
    raise RuntimeError(
        "Missing app credentials. Add them to streamlit/secrets.toml or configure Streamlit secrets."
    )

@st.cache_resource
def get_gemini_client():
    return genai.Client(api_key=GEMINI_API_KEY)

gemini_client = get_gemini_client()

def send_email(to_address, subject, body):
    message = MIMEText(body)
    message["Subject"] = subject
    message["From"] = GMAIL_ADDRESS
    message["To"] = to_address

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
        server.send_message(message)

def render_message(message):
    with st.chat_message(message["role"]):
        if message["kind"] == "text":
            st.write(message["content"])
        elif message["kind"] == "image":
            st.image(message["content"])

def add_message(role, kind, content):
    st.session_state.messages.append({"role": role, "kind": kind, "content": content})
    render_message(st.session_state.messages[-1])

def ask_gemini(parts):
    try:
        return st.session_state.chat.send_message(parts).text
    except Exception as error:
        return f"Sorry, something went wrong: {error}"

# --- Onboarding Form ---
if "onboarded" not in st.session_state:
    st.session_state.onboarded = False

if not st.session_state.onboarded:
    st.title("🧾 ReceiptSnap")
    st.caption("Snap your receipts. Split bills. Email the breakdown.")

    with st.form("onboarding_form"):
        name = st.text_input("Your Name")
        email = st.text_input("Recipient Email Address", placeholder="name@example.com")
        submitted = st.form_submit_button("Start Session 🚀")

        if submitted:
            if not name.strip() or not email.strip():
                st.warning("Please fill in both your name and recipient email address.")
            else:
                st.session_state.name = name.strip()
                st.session_state.email = email.strip()
                st.session_state.chat = gemini_client.chats.create(
                    model=MODEL_NAME,
                    config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
                )
                st.session_state.messages = []
                st.session_state.onboarded = True
                st.rerun()
                st.stop()

    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "name" not in st.session_state:
    st.session_state.name = ""
if "email" not in st.session_state:
    st.session_state.email = ""

# --- Main Interface ---
header_col, button_col = st.columns([5, 2], vertical_alignment="center")

with header_col:
    st.title("🧾 ReceiptSnap")

with button_col:
    send_disabled = len(st.session_state.messages) <= 2
    if st.button("📧 Email Breakdown", disabled=send_disabled, use_container_width=True):
        with st.spinner("Preparing summary..."):
            summary = ask_gemini([SUMMARY_REQUEST_PROMPT])
            try:
                send_email(
                    st.session_state.email,
                    f"ReceiptSnap Summary for {st.session_state.name}",
                    summary,
                )
                st.success("Email sent! 📩")
            except Exception as e:
                st.error(f"Failed to send email: {e}")

st.caption(f"Logged in as {st.session_state.name} | Sending reports to: {st.session_state.email}")

if not st.session_state.messages:
    add_message("assistant", "text", WELCOME_MESSAGE_TEMPLATE.format(name=st.session_state.name))
else:
    for message in st.session_state.messages:
        render_message(message)

user_input = st.chat_input(
    "Upload a receipt image or ask a question...",
    accept_file=True,
    file_type=["jpg", "jpeg", "png"],
)

if user_input:
    photo = user_input.files[0] if user_input.files else None
    text = user_input.text
    parts = []

    if photo is not None:
        photo_bytes = photo.getvalue()
        add_message("user", "image", photo_bytes)
        parts.append(types.Part.from_bytes(data=photo_bytes, mime_type=photo.type))

    if text:
        add_message("user", "text", text)
        parts.append(text)
    elif photo is not None:
        parts.append("Analyze this receipt. Extract itemized prices, total amount, and summary.")

    with st.spinner("Analyzing receipt..."):
        answer = ask_gemini(parts)
        add_message("assistant", "text", answer)