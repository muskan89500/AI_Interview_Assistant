import streamlit as st
import re

# Page Configuration
st.set_page_config(page_title="AI Interview Preparation Assistant", page_icon="🤖")

# Title
st.title("🤖 AI Interview Preparation Assistant")
st.write("Welcome! Practice your interview skills.")

# Candidate Details
st.header("👤 Candidate Details")

# ------------------- QUESTION BANK -------------------
# Each question now has:
#   - "q": the question text
#   - "keywords": key terms/concepts that should appear in a correct answer
#   - "model_answer": a short reference answer shown as feedback
questions = {
    "Python Developer": [
        {
            "q": "What is Python?",
            "keywords": ["interpreted", "high-level", "programming language", "object-oriented", "dynamically typed"],
            "model_answer": "Python is a high-level, interpreted, general-purpose programming language known for readability and dynamic typing."
        },
        {
            "q": "What is a List?",
            "keywords": ["ordered", "mutable", "collection", "index", "square brackets"],
            "model_answer": "A list is an ordered, mutable collection of items in Python, defined using square brackets, e.g. [1, 2, 3]."
        },
        {
            "q": "What is a Dictionary?",
            "keywords": ["key", "value", "pair", "unordered", "mutable", "curly braces"],
            "model_answer": "A dictionary is a mutable collection of key-value pairs in Python, defined using curly braces, e.g. {'key': 'value'}."
        }
    ],
    "Data Analyst": [
        {
            "q": "What is Data Analysis?",
            "keywords": ["inspect", "clean", "transform", "model", "insights", "decision"],
            "model_answer": "Data analysis is the process of inspecting, cleaning, transforming, and modeling data to discover useful insights and support decision-making."
        },
        {
            "q": "What is Pandas?",
            "keywords": ["library", "python", "dataframe", "data manipulation", "analysis"],
            "model_answer": "Pandas is a Python library used for data manipulation and analysis, built around the DataFrame data structure."
        },
        {
            "q": "What is Data Cleaning?",
            "keywords": ["missing", "duplicate", "errors", "inconsistent", "correcting", "removing"],
            "model_answer": "Data cleaning is the process of detecting and correcting (or removing) missing, duplicate, or inconsistent data to improve data quality."
        }
    ],
    "Web Developer": [
        {
            "q": "What is HTML?",
            "keywords": ["markup", "language", "structure", "webpage", "tags"],
            "model_answer": "HTML (HyperText Markup Language) is the standard markup language used to structure content on webpages using tags."
        },
        {
            "q": "What is CSS?",
            "keywords": ["style", "stylesheet", "design", "layout", "presentation"],
            "model_answer": "CSS (Cascading Style Sheets) is used to style and control the layout and presentation of HTML elements."
        },
        {
            "q": "What is JavaScript?",
            "keywords": ["scripting", "programming language", "interactive", "dynamic", "browser"],
            "model_answer": "JavaScript is a scripting/programming language that adds interactivity and dynamic behavior to webpages, running in the browser."
        }
    ]
}

# ------------------- SESSION STATE -------------------
if "start" not in st.session_state:
    st.session_state.start = False

if "question_no" not in st.session_state:
    st.session_state.question_no = 0

if "score" not in st.session_state:
    st.session_state.score = 0

if "name" not in st.session_state:
    st.session_state.name = ""

if "email" not in st.session_state:
    st.session_state.email = ""

if "role" not in st.session_state:
    st.session_state.role = None

if "question_list" not in st.session_state:
    st.session_state.question_list = []

if "feedback_log" not in st.session_state:
    st.session_state.feedback_log = []

# Tracks whether feedback for the current question has already been
# generated, so we can show it before the user clicks "Next".
if "current_feedback" not in st.session_state:
    st.session_state.current_feedback = None


def is_valid_email(email):
    pattern = r"^[\w\.\+\-]+@[\w\-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


def restart_interview():
    st.session_state.start = False
    st.session_state.question_no = 0
    st.session_state.score = 0
    st.session_state.role = None
    st.session_state.question_list = []
    st.session_state.feedback_log = []
    st.session_state.current_feedback = None


def check_answer(user_answer, keywords):
    """
    Detects how many expected keywords/concepts appear in the user's
    answer (case-insensitive, substring match) and classifies the
    answer as Correct / Partially Correct / Incorrect.

    Returns: (label, matched_keywords, score)
    """
    stripped = user_answer.strip()

    if stripped == "":
        return "Blank", [], 0

    answer_lower = stripped.lower()
    matched = [kw for kw in keywords if kw.lower() in answer_lower]
    match_ratio = len(matched) / len(keywords) if keywords else 0

    if match_ratio >= 0.6:
        label = "✅ Correct"
        score = 10
    elif match_ratio >= 0.25:
        label = "🟡 Partially Correct"
        score = 5
    else:
        label = "❌ Incorrect"
        score = 0

    return label, matched, score


# ------------------- CANDIDATE FORM -------------------
# BUG FIX: Name/Email/Role are locked (disabled) once the interview has
# started, so they can no longer be changed mid-interview.
name = st.text_input(
    "Enter Your Name",
    value=st.session_state.name,
    disabled=st.session_state.start
)

email = st.text_input(
    "Enter Your Email",
    value=st.session_state.email,
    disabled=st.session_state.start
)

role = st.selectbox(
    "Select Job Role",
    list(questions.keys()),
    index=list(questions.keys()).index(st.session_state.role) if st.session_state.role else 0,
    disabled=st.session_state.start
)

# ------------------- START BUTTON -------------------
if not st.session_state.start:
    if st.button("🎯 Start Interview"):

        if name.strip() == "" or email.strip() == "":
            st.error("Please enter your Name and Email.")
        elif not is_valid_email(email):
            # BUG FIX: proper email format validation, not just "non-empty"
            st.error("Please enter a valid email address.")
        else:
            st.session_state.name = name
            st.session_state.email = email
            st.session_state.role = role
            st.session_state.question_list = questions[role]
            st.session_state.start = True
            st.rerun()

# ------------------- INTERVIEW SECTION -------------------
if st.session_state.start:

    st.success(f"Welcome {st.session_state.name}")
    st.write(f"**Role:** {st.session_state.role}")

    # BUG FIX: question_list now comes from session_state, so it always
    # exists even after a refresh — this removes the NameError crash.
    question_list = st.session_state.question_list

    if st.session_state.question_no < len(question_list):

        current_q = question_list[st.session_state.question_no]

        st.header(f"Question {st.session_state.question_no + 1} of {len(question_list)}")
        st.progress((st.session_state.question_no) / len(question_list))
        st.write(current_q["q"])

        st.info("⏰ Time Limit : 30 Seconds")

        answer = st.text_area(
            "Write Your Answer",
            key=f"answer_{st.session_state.question_no}"
        )

        col1, col2 = st.columns([1, 1])

        with col1:
            check_clicked = st.button("🔍 Check Answer")

        with col2:
            next_clicked = st.button("Next ➡️")

        # ---- ANSWER DETECTION / CORRECTION ----
        if check_clicked:
            label, matched, _ = check_answer(answer, current_q["keywords"])

            if label == "Blank":
                st.warning("Please write an answer before checking it.")
            else:
                if label == "✅ Correct":
                    st.success(f"{label} — good answer!")
                elif label == "🟡 Partially Correct":
                    st.warning(f"{label} — you covered some key points, but missed a few.")
                else:
                    st.error(f"{label} — this answer misses most key points.")

                if matched:
                    st.write(f"**Keywords detected:** {', '.join(matched)}")
                else:
                    st.write("**Keywords detected:** none")

                st.write(f"**Model Answer:** {current_q['model_answer']}")

        # ---- MOVE TO NEXT QUESTION ----
        if next_clicked:

            label, matched, points = check_answer(answer, current_q["keywords"])

            if label == "Blank":
                st.warning("Please write an answer before continuing (0 marks given for blank answers).")

            st.session_state.score += points
            st.session_state.feedback_log.append({
                "question": current_q["q"],
                "answer": answer.strip(),
                "result": label,
                "matched_keywords": matched,
                "points": points,
                "model_answer": current_q["model_answer"]
            })

            st.session_state.question_no += 1
            st.rerun()

    # Interview Completed
    else:

        st.header("🎉 Interview Completed")
        st.success(f"Final Score : {st.session_state.score}")

        progress = st.session_state.score / (len(question_list) * 10)
        st.progress(min(progress, 1.0))

        # ---- DETAILED FEEDBACK / ANSWER REVIEW ----
        st.subheader("📋 Answer Review")
        for i, item in enumerate(st.session_state.feedback_log, start=1):
            with st.expander(f"Q{i}: {item['question']}  —  {item['result']} ({item['points']} pts)"):
                st.write(f"**Your Answer:** {item['answer'] if item['answer'] else '_(blank)_'}")
                st.write(f"**Keywords Detected:** {', '.join(item['matched_keywords']) if item['matched_keywords'] else 'none'}")
                st.write(f"**Model Answer:** {item['model_answer']}")

        # ---- DOWNLOADABLE RESULT (includes correctness breakdown) ----
        result_lines = [
            f"Candidate Name : {st.session_state.name}",
            f"Email : {st.session_state.email}",
            f"Role : {st.session_state.role}",
            "",
            f"Final Score : {st.session_state.score}",
            "",
            "Answer Review:",
        ]
        for i, item in enumerate(st.session_state.feedback_log, start=1):
            result_lines.append(f"\nQ{i}: {item['question']}")
            result_lines.append(f"Your Answer: {item['answer'] if item['answer'] else '(blank)'}")
            result_lines.append(f"Result: {item['result']} ({item['points']} pts)")
            result_lines.append(f"Keywords Detected: {', '.join(item['matched_keywords']) if item['matched_keywords'] else 'none'}")
            result_lines.append(f"Model Answer: {item['model_answer']}")

        result = "\n".join(result_lines)

        st.download_button(
            "📥 Download Result",
            result,
            file_name="Interview_Result.txt",
            mime="text/plain"
        )

        # BUG FIX: added a Restart button so users can retake the
        # interview without needing to refresh the whole page.
        if st.button("🔄 Restart Interview"):
            restart_interview()
            st.rerun()
