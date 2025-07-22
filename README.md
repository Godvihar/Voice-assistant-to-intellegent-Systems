# Voice-assistant-to-intelligent-Systems

## Project Description
**Voice Assistant to Intelligent Systems** is a powerful Python-based desktop assistant that empowers users to control their computer using natural voice commands. It provides sign language output, generates images from prompts, automates tasks, and delivers real-time feedback through both audio and visual channels—making technology more accessible, creative, and efficient for everyone.

### Key Features
- **Voice Command Recognition:** Speak to control your PC, launch apps, manage files, set alarms, and more.
- **Sign Language Output:** Converts responses into sign language GIFs/images for accessibility.
- **Image Generation:** Create images from your descriptions using AI models or APIs.
- **Task Automation:** Open apps, manage folders, generate PDFs, and automate daily routines.
- **Web Search & Info Retrieval:** Real-time search and spoken summaries of results.
- **Email Sending:** Send emails via voice, with smart extraction of recipient, subject, and message.
- **Alarms & Reminders:** Set alarms and reminders hands-free.
- **User-Friendly GUI:** Clean Tkinter interface for all interactions, including sign language and images.
- **Real-Time Feedback:** Immediate responses via speech (pyttsx3) and on-screen visuals.
- **Accessibility:** Designed for users with different abilities—voice, text, and sign language support.

### Technologies Used
- **Python 3.x** (core language)
- **SpeechRecognition, PyAudio** (voice input)
- **pyttsx3** (text-to-speech)
- **Tkinter** (GUI)
- **smtplib, email** (email backend)
- **PIL, requests** (image generation/manipulation)
- **os, sys, subprocess, threading, queue, datetime, time, json, logging** (automation, concurrency, error handling)

### Quick Start
1. **Clone the repository.**
2. **Install dependencies:**
   ```bash
   pip install -r Requirements.txt
   ```
3. **Create your `.env` file:**
   - Use `.env.example` as a template and fill in your credentials and API keys.
4. **Run the assistant:**
   ```bash
   python Main.py
   ```

### Accessibility & Extensibility
- Works offline for most features; some (like cloud speech/image APIs) require internet.
- Modular design: Easily add new features like smart home integration or more languages.

---

**Make your desktop smarter, more accessible, and more creative with Voice Assistant to Intelligent Systems!**
