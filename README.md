 <div align="center">

<img src="https://em-content.zobj.net/source/microsoft-teams/337/robot_1f916.png" width="90" />

# AI Interview Preparation Assistant

**Practice smarter. Answer better. Get hired.**

An interactive AI-powered platform that helps students and job seekers practice technical interviews with instant, structured feedback — no human interviewer required.

<br>

[![Live Demo](https://img.shields.io/badge/🚀_Live_Demo-Try_it_Now-FF4B4B?style=for-the-badge)](https://aiinterviewassistant-cune8tgx7mxxgslvfk2yvc.streamlit.app/)

![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=flat-square&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=flat-square)
![PRs](https://img.shields.io/badge/PRs-Welcome-blueviolet?style=flat-square)

</div>

<br>

---

# 📚 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Demo](#-demo)
- [Tech Stack](#️-tech-stack)
- [Getting Started](#-getting-started)
- [AI-Based Smart Checking](#-ai-based-smart-checking-optional)
- [Roadmap](#-roadmap)
- [Author](#-author)

---

# 🌟 Overview

Candidates register, choose a job role, answer real interview-style questions under a timer, and get **instant feedback** — Correct, Partially Correct, or Incorrect — along with a model answer to learn from. At the end, they get a full performance breakdown and a downloadable report.

> Built for anyone preparing for technical interviews who wants a quick, judgment-free way to practice.

---

# ✨ Features

<table>
<tr>
<td width="50%" valign="top">

**👤 Candidate Experience**
- Name / email / role registration with validation
- 5 job roles: Python, Data Analyst, Web Dev, Java, SQL
- Difficulty tags on every question
- ⏰ Live 30-second countdown timer

</td>
<td width="50%" valign="top">

**🧠 Smart Evaluation**
- ✅ Instant answer correctness detection
- 🤖 Optional AI-based semantic grading (Claude)
- 📊 Real-time score & progress sidebar
- 📋 Full answer review with model answers

</td>
</tr>
<tr>
<td width="50%" valign="top">

**📥 Results**
- Downloadable `.txt` performance report
- Score breakdown per question
- Key points detected for every answer

</td>
<td width="50%" valign="top">

**🔄 Flexibility**
- Restart anytime, no page refresh needed
- Works instantly — no login/setup required
- Gracefully falls back if AI isn't configured

</td>
</tr>
</table>

---

## 🎬 Demo

<div align="center">

**[👉 Click here to try the live app](https://aiinterviewassistant-cune8tgx7mxxgslvfk2yvc.streamlit.app/)**

*No installation. No sign-up. Just open and start practicing.*

</div>

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Language** | Python 🐍 |
| **Framework** | Streamlit |
| **AI Grading** *(optional)* | Anthropic Claude API |
| **Deployment** | Streamlit Community Cloud |

---

# 🚀 Getting Started

# Option 1 — Use it instantly (recommended)
No setup needed:
👉 **[Open the live app](https://aiinterviewassistant-cune8tgx7mxxgslvfk2yvc.streamlit.app/)**

# Option 2 — Run locally

```bash
# Clone the repo
git clone https://github.com/muskan89500/AI_Interview_Assistant.git
cd AI_Interview_Assistant

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

App opens automatically at `http://localhost:8501` 🎉

---
## 🔑 AI-Based Smart Checking *(Optional)*

By default, answers are graded using **keyword matching** — works instantly with zero setup.

Want smarter, human-like grading that understands paraphrased answers?

1. Get a free API key from [console.anthropic.com](https://console.anthropic.com)
2. Add it as `ANTHROPIC_API_KEY` under your Streamlit app's **Secrets**
3. Done — the app auto-detects it and switches to AI grading ✨

> If no key is set, the app silently falls back to keyword checking. Nothing breaks either way.

---

# 🗺️ Roadmap

- [ ] 🎙️ Voice-based answers
- [ ] 📈 Difficulty-adaptive question flow
- [ ] 🗂️ Results history dashboard
- [ ] 🌐 More job roles & languages

---

# 🙋 Author

<div align="center">

Built with ❤️ by **Muskan**

[![GitHub](https://img.shields.io/badge/GitHub-muskan89500-181717?style=flat-square&logo=github)](https://github.com/muskan89500)

</div>

---

<div align="center">

### ⭐ If this project helped you, consider giving it a star!

</div>

 


