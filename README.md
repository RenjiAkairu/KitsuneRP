# 🦊 KitsuneRP

**A modern Discord Rich Presence tool designed by Renji, powered by AI-Assisted Development.**

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Beta-orange)

![Platform](https://img.shields.io/badge/Platform-Windows-blue)
![Platform](https://img.shields.io/badge/Linux-Planned-yellow)
![Platform](https://img.shields.io/badge/macOS-Not%20Planned-lightgrey)

## ✨ Preview
See KitsuneRP in action!

| Application Interface | Discord Profile Result |
| :---: | :---: |
| <img src="https://github.com/user-attachments/assets/df6a0d26-6452-45d6-8152-f22825c875b1" width="450" /> | <img src="https://github.com/user-attachments/assets/0a46deb6-3b5b-402b-9951-09bb7284386f" width="220" /> |

## 📖 About
This project provides a customizable Discord Rich Presence (RP) with a modern, dark-themed UI built using **CustomTkinter**. It features a preset management system, allowing you to switch between different statuses easily.

* **Concept & Logic Design:** Renji
* **Implementation:** Assisted by AI (Antigravity/Gemini) focusing on modern UI/UX and OOP practices.

---

## 💻 Compatibility / Supported Platforms
* ✅ **Windows:** Fully supported (Download .exe in Releases)
* 🚧 **Linux:** Planned (Currently works via Source Code)
* ❌ **macOS:** Not planned yet (Requires specific hardware/license)

---

## ⚠️ Safety Note regarding Antivirus / VirusTotal
If you download the `.exe` version, your antivirus (or VirusTotal) might flag it as a threat (Generic/Trojan).
**This is a False Positive.**

* **Why does this happen?** This app is built with Python and compiled using `PyInstaller`. Many antivirus engines automatically flag uncertified Python executables that interact with system processes (like checking CPU/RAM) as suspicious.
* **Transparency:** This project is Open Source. If you are uncomfortable running the `.exe`, you are encouraged to **review the source code (`main.py`)** and run it directly using Python.

---

## ⚙️ How to Setup (Getting Client ID)
To use this app, you need a **Discord Application ID**. It's free and takes 1 minute to get.

1.  Go to the [Discord Developer Portal](https://discord.com/developers/applications).
2.  Log in with your Discord account.
3.  Click the **"New Application"** button (top right).
4.  Give it a name (e.g., *"Playing with Foxes"* or whatever you want to show on your profile).
5.  Agree to the terms and click **Create**.
6.  Go to **OAuth2** tab on left panel.
7.  Copy the **"Client ID"** shown on the screen.
8.  Paste this ID into the **Client ID** box in the app.

*(Optional)* Go to the **"Rich Presence" -> "Art Assets"** tab in the Developer Portal to upload images if you want to use custom pictures.

---

## 🚀 How to Run

### Option 1: Download .exe (Easiest)
1.  Go to the **Releases** page on this repository.
2.  Download `KitsuneRP.exe`.
3.  Run the app (You might need to "Run anyway" if Windows Defender warns you).

### Option 2: Run from Source (For Developers)
"Compatible with Windows, Linux, and macOS (Python 3.10+ required)"

If you prefer running the Python script directly:

1.  Clone this repository.
2.  Install requirements:
    ```bash
    pip install -r requirements.txt
    ```
3.  Run the script:
    ```bash
    python main.py
    ```

---

## 🤝 Credits & Acknowledgements

* **Concept & Logic Design:** Renji
* **Development Assistant:** AI (Antigravity/Gemini)
    * *Role:* Code generation, refactoring, and implementation support.
* **Libraries:**
    * `customtkinter` (Modern UI)
    * `pypresence` (Discord RPC connection)

---

## 📄 License
This project is licensed under the **MIT License** - feel free to use, modify, and distribute with attribution.
