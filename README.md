# 🤖 AI Interview Preparation Assistant

A Streamlit web app that helps students and job-seekers practice interview
questions, get their answers graded, and track their progress over time —
across both **core CS fundamentals** (Arrays, Linked Lists, Stacks, Queues,
DBMS, OS) and **role-specific tracks** (Python, Data Analyst, Web Dev, Java,
SQL).

Answers can be graded two ways:
- **AI-based semantic grading** using Claude, if you provide an API key
- **Keyword-based grading** as an automatic fallback with zero setup

Everything runs from a single `app.py` file, with progress saved locally in
a JSON file so your scores persist across sessions.

---

# ✨ Features

| Page | What it does |
|---|---|
| 🏠 **Home** | Live stats (students practicing, questions available, success rate) and quick links into every feature |
| 👤 **Student Profile** | Save your name, email, preferred role, branch, and year — this is what ties your progress together |
| 📊 **Skill Assessment** | Untimed, multi-topic quickfire quiz — pick one or more roles and get graded instantly |
| 💡 **Interview Questions** | A focused, timed mock-interview flow for a single role, with a 30s-per-question timer |
| 📈 **Progress Tracker** | Per-topic score table (Current vs. Target) plus an overall interview-readiness verdict |
| 📉 **Dashboard** | Total attempts, overall score, a topic breakdown bar chart, weakest topic, and recent attempt history |
| 🗺️ **AI Roadmap** | Auto-detects weak topics (<50%) and suggests what to study next — with an optional Claude-generated personalized paragraph |

---

# 🖼️ Screenshots

_Add your own screenshots here, e.g.:_

```md
![Home Page](screenshots/home.png)
![Progress Tracker](screenshots/progress_tracker.png)
```

---

# 🧱 Tech Stack

- [Streamlit](https://streamlit.io/) — UI framework
- [Anthropic Claude API](https://docs.claude.com/) — optional semantic answer grading & AI roadmap generation
- Plain JSON file storage — no database required

---
# 🚀 Getting Started

# 1. Clone the repo
```bash
git clone https://github.com/<your-username>/ai-interview-prep-assistant.git
cd ai-interview-prep-assistant
```

# 2. Install dependencies
```bash
pip install streamlit anthropic
```

# 3. (Optional) Enable AI-based grading
Create `.streamlit/secrets.toml` in the project root:
```toml
ANTHROPIC_API_KEY = "your-api-key-here"
```
Without this file, the app works fully out of the box using keyword-based
grading — nothing breaks, you just won't get semantic grading or the
AI-generated roadmap paragraph.

# 4. Run the app
```bash
streamlit run app.py
```
The app will open at `http://localhost:8501`.

---

# 📂 Project Structure

```
.
├── app.py               # Full application — question bank, storage, grading, and all pages
├── students_data.json   # Auto-created on first run; stores profiles + progress (gitignored)
└── .streamlit/
    └── secrets.toml      # Optional — your ANTHROPIC_API_KEY (gitignored)
```

> `app.py` is intentionally a single file for easy deployment (e.g. Streamlit
> Community Cloud) and simple copy/paste updates. It's organized internally
> into five clearly commented sections: Question Bank, Persistence, Grading,
> Pages, and App Entry/Navigation.

---

# 💾 How Progress Tracking Works

Every question is tagged with a **topic** (e.g. `Arrays`, `OOP Concepts`,
`Database Design`). Whenever you complete a Skill Assessment or Interview,
your score is added to that topic's running total in `students_data.json`,
keyed by your email. The Progress Tracker, Dashboard, and AI Roadmap pages
all read from that same per-topic data, so they always stay in sync.

**Readiness scoring** (tweakable in the `readiness_from_rows()` function):
| Average Score | Verdict |
|---|---|
| 80%+ | 🎉 You are Interview Ready! |
| 50–79% | 📈 You are improving, but still need practice. |
| < 50% | 🔴 You need more practice before your interview. |

---

# ⚠️ Notes Before Deploying Publicly

- `students_data.json` is **plain, unencrypted JSON** — fine for a personal
  project, class assignment, or demo, but don't use it to store real users'
  sensitive data in production without adding proper security.
- Add `students_data.json` and `.streamlit/secrets.toml` to your
  `.gitignore` so you don't accidentally commit user data or your API key.

```gitignore
students_data.json
.streamlit/secrets.toml
__pycache__/
```

---

# 🛣️ Roadmap / Ideas for Contribution

- [ ] Export progress/results as PDF
- [ ] Add more roles and topics to the question bank
- [ ] Auto-submit answers when the timer hits 0
- [ ] Leaderboard across students
- [ ] Voice-based answer input

---


