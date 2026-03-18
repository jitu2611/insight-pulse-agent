# 📡 InsightPulse Agent

**InsightPulse** is an autonomous AI news curator designed to cut through the noise. Unlike a standard news aggregator, InsightPulse "reads" articles through the lens of your chosen **Digital Persona** and tells you exactly *why* each story matters to you.

---

## ✨ Features

*   **👤 Persona-Driven Reasoning:** Define your role, interests, and tone in `config.yaml`. The agent filters and analyzes news accordingly.
*   **🧠 Multi-LLM Support:** Native support for **OpenAI (GPT-4o)**, **Anthropic (Claude 3.5)**, and **Google (Gemini 1.5)**.
*   **💎 Premium CLI:** A beautiful terminal-based dashboard built with `Rich`.
*   **📱 Mobile Dispatch:** Sends a daily summary of the top 3 high-value insights directly to your iPhone via [ntfy.sh](https://ntfy.sh).
*   **🌐 Multi-Source Aggegator:** Pulls from any standard RSS/Atom feeds.

---

## 🛠️ Quick Start

### 1. Installation
Clone this repository and set up a virtual environment:
```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configuration
*   **`config.yaml`**: Edit this file to update your Name, Role, Interests, and desired RSS feed URLs.
*   **`.env`**: Rename `.env.example` to `.env` and add your API keys (OpenAI, Anthropic, or Gemini).

### 3. Mobile Setup (Optional)
To receive insights on your iPhone:
1.  Download the **ntfy** app from the App Store.
2.  Subscribe to your unique topic (default: `jitu_insight_pulse_99`).
3.  Ensure `notifications.enabled` is `true` in `config.yaml`.

---

## 🚀 Usage

Run the agent daily to get your pulse check:
```powershell
.\.venv\Scripts\activate
python main.py
```

---

## 🏗️ Project Structure

*   `main.py`: The entry point.
*   `app/agent.py`: The AI reasoning engine (supports OpenAI, Claude, Gemini).
*   `app/feeds.py`: RSS fetching and parsing logic.
*   `app/notify.py`: ntfy.sh dispatch system.
*   `app/ui.py`: CLI display engine.

---

## 🔒 Security
InsightPulse is built with privacy in mind. Your API keys are stored in a local `.env` file that is listed in `.gitignore` to prevent accidental uploads to GitHub.

---

*Made with ❤️ by [jitu2611](https://github.com/jitu2611)*
