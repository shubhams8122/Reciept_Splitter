# ReceiptSnap

ReceiptSnap is a Streamlit-based receipt analysis and expense-splitting web app. It lets a user upload a receipt image, ask questions about it, get a structured summary, and send the final breakdown via email.

## Live Demo
https://recieptsplitterbysingh.streamlit.app/

## Overview

This app is designed for quick receipt processing and bill splitting. A user enters their name and email, uploads a receipt, and then interacts with a Gemini-powered assistant that can:

- read and analyze receipt images
- extract vendor and item details
- calculate totals, tax, and final amount
- provide per-person bill splits
- summarize the conversation into a clean email-ready message

## Features

- onboarding form with name and recipient email
- receipt image upload via chat input
- AI-powered receipt parsing using Gemini
- conversation history within the Streamlit session
- summary generation for email delivery
- Gmail SMTP email sending

## Tech Stack

- Python
- Streamlit
- Google Gemini API via google-genai
- Gmail SMTP for outbound email delivery
- TOML-based secrets configuration

## Project Structure

- `app.py` – main Streamlit app and core logic
- `prompts.py` – system prompt, welcome text, and summary prompt
- `requirement.txt` – Python dependencies
- `streamlit/secrets.toml` – local secrets file for app credentials
- `.streamlit/secrets.toml` – fallback secret location used for runtime startup

## Workflow

1. User opens the app and enters their name and email address.
2. A Gemini chat session is created with the app’s system instructions.
3. The user uploads a receipt image or sends a question in the chat.
4. The app sends the receipt and prompt to Gemini for parsing and understanding.
5. Gemini extracts item details, totals, taxes, and any split logic requested by the user.
6. The user can review the breakdown and click the summary button to email the final result.

## Files in Use

### app.py

This is the main entry point. It handles:

- Streamlit page configuration
- loading environment credentials/secrets
- creating the Gemini client
- onboarding and session-state management
- rendering chat messages
- sending the final summary email

### prompts.py

This file stores the prompts used by the assistant:

- `SYSTEM_PROMPT`: tells the AI its role and rules
- `WELCOME_MESSAGE_TEMPLATE`: greeting shown to the user
- `SUMMARY_REQUEST_PROMPT`: instruction for generating an email-friendly summary

### requirement.txt

Includes the project dependencies:

- `streamlit`
- `google-genai`

## Setup Instructions

### 1. Create a virtual environment

```bash
python -m venv venv
```

### 2. Activate the virtual environment

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirement.txt
```

### 4. Configure secrets

Create a secrets file with your API and Gmail credentials.

Example:

```toml
GEMINI_API_KEY = "your-gemini-api-key"
GMAIL_ADDRESS = "your-email@gmail.com"
GMAIL_APP_PASSWORD = "your-16-char-app-password"
```

The app is configured to read from the local project secret file and also supports the standard Streamlit secret path.

## Run the App

From the project root:

```bash
streamlit run app.py
```

If `streamlit` is not on the PATH in your environment, run:

```bash
.\venv\Scripts\python.exe -m streamlit run app.py
```

## Example Use Case

A user uploads a restaurant receipt, asks to split the bill across 3 people, and then receives a clean itemized summary that can be emailed to the selected recipient.
