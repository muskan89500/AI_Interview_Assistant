import streamlit as st
import re
import time
import json

# Page Configuration
st.set_page_config(page_title="AI Interview Preparation Assistant", page_icon="🤖", layout="centered")

# Title
st.title("🤖 AI Interview Preparation Assistant")
st.write("Welcome! Practice your interview skills.")

# ------------------- OPTIONAL: ANTHROPIC CLIENT (for smart AI checking) -------------------
# If an ANTHROPIC_API_KEY is configured in Streamlit secrets, answers are graded
# using Claude for semantic understanding (not just keyword matching).
# If no key is found, the app automatically falls back to keyword-based checking.
AI_AVAILABLE = False
client = None
try:
    import anthropic
    api_key = st.secrets.get("ANTHROPIC_API_KEY", None)
    if api_key:
        client = anthropic.Anthropic(api_key=api_key)
        AI_AVAILABLE = True
except Exception:
    AI_AVAILABLE = False


# ------------------- QUESTION BANK -------------------
# Each question has: text, difficulty, keywords (fallback grading), model_answer
questions = {
    "Python Developer": [
        {"q": "What is Python?", "difficulty": "Easy",
         "keywords": ["interpreted", "high-level", "programming language", "object-oriented", "dynamically typed"],
         "model_answer": "Python is a high-level, interpreted, general-purpose programming language known for readability and dynamic typing."},
        {"q": "What is a List?", "difficulty": "Easy",
         "keywords": ["ordered", "mutable", "collection", "index", "square brackets"],
         "model_answer": "A list is an ordered, mutable collection of items in Python, defined using square brackets, e.g. [1, 2, 3]."},
        {"q": "What is a Dictionary?", "difficulty": "Medium",
         "keywords": ["key", "value", "pair", "unordered", "mutable", "curly braces"],
         "model_answer": "A dictionary is a mutable collection of key-value pairs in Python, defined using curly braces, e.g. {'key': 'value'}."},
    ],
    "Data Analyst": [
        {"q": "What is Data Analysis?", "difficulty": "Easy",
         "keywords": ["inspect", "clean", "transform", "model", "insights", "decision"],
         "model_answer": "Data analysis is the process of inspecting, cleaning, transforming, and modeling data to discover useful insights and support decision-making."},
        {"q": "What is Pandas?", "difficulty": "Easy",
         "keywords": ["library", "python", "dataframe", "data manipulation", "analysis"],
         "model_answer": "Pandas is a Python library used for data manipulation and analysis, built around the DataFrame data structure."},
        {"q": "What is Data Cleaning?", "difficulty": "Medium",
         "keywords": ["missing", "duplicate", "errors", "inconsistent", "correcting", "removing"],
         "model_answer": "Data cleaning is the process of detecting and correcting (or removing) missing, duplicate, or inconsistent data to improve data quality."},
    ],
    "Web Developer": [
        {"q": "What is HTML?", "difficulty": "Easy",
         "keywords": ["markup", "language", "structure", "webpage", "tags"],
         "model_answer": "HTML (HyperText Markup Language) is the standard markup language used to structure content on webpages using tags."},
        {"q": "What is CSS?", "difficulty": "Easy",
         "keywords": ["style", "stylesheet", "design", "layout", "presentation"],
         "model_answer": "CSS (Cascading Style Sheets) is used to style and control the layout and presentation of HTML elements."},
        {"q": "What is JavaScript?", "difficulty": "Medium",
         "keywords": ["scripting", "programming language", "interactive", "dynamic", "browser"],
         "model_answer": "JavaScript is a scripting/programming language that adds interactivity and dynamic behavior to webpages, running in the browser."},
    ],
    "Java Developer": [
        {"q": "What is Java?", "difficulty": "Easy",
         "keywords": ["object-oriented", "platform-independent", "programming language", "jvm", "compiled"],
         "model_answer": "Java is an object-oriented, platform-independent programming language that runs on the Java Virtual Machine (JVM)."},
        {"q": "What is a Class in Java?", "difficulty": "Easy",
         "keywords": ["blueprint", "object", "template", "properties", "methods"],
         "model_answer": "A class is a blueprint/template for creating objects, defining their properties (fields) and behaviors (methods)."},
        {"q": "What is Inheritance?", "difficulty": "Medium",
         "keywords": ["reuse", "parent", "child", "extends", "properties", "methods"],
         "model_answer": "Inheritance allows a child class to reuse and extend the properties and methods of a parent class using the 'extends' keyword."},
    ],
    "SQL Developer": [
        {"q": "What is SQL?", "difficulty": "Easy",
         "keywords": ["structured query language", "database", "query", "manage", "relational"],
         "model_answer": "SQL (Structured Query Language) is used to query, manage, and manipulate data in relational databases."},
        {"q": "What is a Primary Key?", "difficulty": "Easy",
         "keywords": ["unique", "identifier", "row", "not null", "table"],
         "model_answer": "A primary key is a column (or set of columns) that uniquely identifies each row in a table and cannot be null."},
        {"q": "What is a JOIN?", "difficulty": "Medium",
         "keywords": ["combine", "tables", "related", "column", "rows"],
         "model_answer": "A JOIN combines rows from two or more tables based on a related column between them."},
    ],
}

TIME_LIMIT_SECONDS = 30

# ------------------- SESSION STATE -------------------
defaults = {
    "start": False,
    "question_no": 0,
    "score": 0,
    "name": "",
    "email": "",
    "role": None,
    "question_list": [],
    "feedback_log": [],
    "question_start_time": None,
    "use_ai_checking": AI_AVAILABLE,
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


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
    st.session_state.question_start_time = None


def keyword_check(user_answer, keywords):
    """Fallback grading: substring keyword matching."""
    stripped = user_answer.strip()
    if stripped == "":
        return "Blank", [], 0, "Please write an answer before checking it."

    answer_lower = stripped.lower()
    matched = [kw for kw in keywords if kw.lower() in answer_lower]
    ratio = len(matched) / len(keywords) if keywords else 0

    # BUG FIX: previously a short-but-correct answer (e.g. matching just 1 of 5
    # keywords) could score below the "Partial" threshold and be marked
    # Incorrect. Now, matching ANY keyword guarantees at least Partial credit,
    # and a strong majority match (40%+) counts as fully Correct.
    if ratio >= 0.4:
        return "✅ Correct", matched, 10, "Good answer! You covered the key points."
    elif len(matched) >= 1:
        return "🟡 Partially Correct", matched, 5, "You're on the right track, but try to include more detail."
    else:
        return "❌ Incorrect", matched, 0, "This answer misses the key points. Check the model answer below."


def ai_check_answer(question_text, user_answer, model_answer):
    """
    Smarter semantic grading using Claude. Understands paraphrased / short-but-correct
    answers instead of relying only on exact keyword matches.
    Returns: (label, matched_points, score, feedback)
    """
    stripped = user_answer.strip()
    if stripped == "":
        return "Blank", [], 0, "Please write an answer before checking it."

    try:
        prompt = f"""You are grading a candidate's interview answer.

Question: {question_text}
Model/Reference Answer: {model_answer}
Candidate's Answer: {stripped}

Grade the candidate's answer for correctness and completeness compared to the reference answer,
even if worded differently. Respond ONLY with valid JSON, no extra text, in this exact format:
{{"verdict": "Correct" or "Partial" or "Incorrect", "score": <0, 5, or 10>, "feedback": "<one short sentence of feedback>", "key_points_covered": ["point1", "point2"]}}"""

        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}]
        )

        text = response.content[0].text.strip()
        text = re.sub(r"^```json|```$", "", text).strip()
        data = json.loads(text)

        verdict = data.get("verdict", "Incorrect")
        score = int(data.get("score", 0))
        feedback = data.get("feedback", "")
        points = data.get("key_points_covered", [])

        label_map = {"Correct": "✅ Correct", "Partial": "🟡 Partially Correct", "Incorrect": "❌ Incorrect"}
        label = label_map.get(verdict, "❌ Incorrect")

        return label, points, score, feedback

    except Exception:
        # If the AI call fails for any reason, gracefully fall back to keyword checking
        return None  # signal to caller to use fallback


def grade_answer(question_text, user_answer, keywords, model_answer):
    """Routes to AI grading if available/enabled, else keyword grading."""
    if st.session_state.use_ai_checking and AI_AVAILABLE:
        result = ai_check_answer(question_text, user_answer, model_answer)
        if result is not None:
            return result
    return keyword_check(user_answer, keywords)


# ------------------- SIDEBAR: LIVE PROGRESS -------------------
with st.sidebar:
    st.header("📊 Progress")
    if st.session_state.start and st.session_state.question_list:
        total = len(st.session_state.question_list)
        st.metric("Question", f"{min(st.session_state.question_no + 1, total)} / {total}")
        st.metric("Score So Far", st.session_state.score)
        st.progress(min(st.session_state.question_no / total, 1.0))
    else:
        st.write("Interview not started yet.")

    st.divider()
    if AI_AVAILABLE:
        st.success("🤖 AI-based smart checking: ON")
        st.session_state.use_ai_checking = st.checkbox(
            "Use AI checking (semantic)", value=st.session_state.use_ai_checking
        )
    else:
        st.info("🤖 AI checking unavailable — using keyword-based checking.\n\nAdd `ANTHROPIC_API_KEY` in Streamlit secrets to enable smarter grading.")


# ------------------- CANDIDATE FORM -------------------
st.header("👤 Candidate Details")

name = st.text_input("Enter Your Name", value=st.session_state.name, disabled=st.session_state.start)
email = st.text_input("Enter Your Email", value=st.session_state.email, disabled=st.session_state.start)
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
            st.error("Please enter a valid email address.")
        else:
            st.session_state.name = name
            st.session_state.email = email
            st.session_state.role = role
            st.session_state.question_list = questions[role]
            st.session_state.start = True
            st.session_state.question_start_time = time.time()
            st.rerun()

# ------------------- INTERVIEW SECTION -------------------
if st.session_state.start:

    st.success(f"Welcome {st.session_state.name}")
    st.write(f"**Role:** {st.session_state.role}")

    question_list = st.session_state.question_list

    if st.session_state.question_no < len(question_list):

        current_q = question_list[st.session_state.question_no]

        if st.session_state.question_start_time is None:
            st.session_state.question_start_time = time.time()

        elapsed = time.time() - st.session_state.question_start_time
        remaining = max(0, int(TIME_LIMIT_SECONDS - elapsed))

        st.header(f"Question {st.session_state.question_no + 1} of {len(question_list)}")
        st.caption(f"Difficulty: {current_q['difficulty']}")
        st.progress((st.session_state.question_no) / len(question_list))
        st.write(current_q["q"])

        timer_col, _ = st.columns([1, 3])
        with timer_col:
            if remaining > 0:
                st.info(f"⏰ Time Left: {remaining}s")
            else:
                st.warning("⏰ Time's up! Please submit your answer.")

        answer = st.text_area("Write Your Answer", key=f"answer_{st.session_state.question_no}")

        col1, col2 = st.columns([1, 1])
        with col1:
            check_clicked = st.button("🔍 Check Answer")
        with col2:
            next_clicked = st.button("Next ➡️")

        # ---- ANSWER DETECTION / CORRECTION ----
        if check_clicked:
            with st.spinner("Checking your answer..."):
                label, matched, _, feedback = grade_answer(
                    current_q["q"], answer, current_q["keywords"], current_q["model_answer"]
                )

            if label == "Blank":
                st.warning(feedback)
            else:
                if label == "✅ Correct":
                    st.success(f"{label} — {feedback}")
                elif label == "🟡 Partially Correct":
                    st.warning(f"{label} — {feedback}")
                else:
                    st.error(f"{label} — {feedback}")

                st.write(f"**Key points detected:** {', '.join(matched) if matched else 'none'}")
                st.write(f"**Model Answer:** {current_q['model_answer']}")

        # ---- MOVE TO NEXT QUESTION ----
        if next_clicked:
            with st.spinner("Scoring your answer..."):
                label, matched, points, feedback = grade_answer(
                    current_q["q"], answer, current_q["keywords"], current_q["model_answer"]
                )

            if label == "Blank":
                st.warning("Please write an answer before continuing (0 marks given for blank answers).")

            st.session_state.score += points
            st.session_state.feedback_log.append({
                "question": current_q["q"],
                "answer": answer.strip(),
                "result": label,
                "matched_keywords": matched,
                "points": points,
                "model_answer": current_q["model_answer"],
                "feedback": feedback,
            })

            st.session_state.question_no += 1
            st.session_state.question_start_time = time.time()
            st.rerun()

    # Interview Completed
    else:
        st.header("🎉 Interview Completed")
        st.success(f"Final Score : {st.session_state.score}")

        progress = st.session_state.score / (len(question_list) * 10)
        st.progress(min(progress, 1.0))

        st.subheader("📋 Answer Review")
        for i, item in enumerate(st.session_state.feedback_log, start=1):
            with st.expander(f"Q{i}: {item['question']}  —  {item['result']} ({item['points']} pts)"):
                st.write(f"**Your Answer:** {item['answer'] if item['answer'] else '_(blank)_'}")
                st.write(f"**Feedback:** {item.get('feedback', '')}")
                st.write(f"**Key Points Detected:** {', '.join(item['matched_keywords']) if item['matched_keywords'] else 'none'}")
                st.write(f"**Model Answer:** {item['model_answer']}")

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
            result_lines.append(f"Feedback: {item.get('feedback', '')}")
            result_lines.append(f"Key Points Detected: {', '.join(item['matched_keywords']) if item['matched_keywords'] else 'none'}")
            result_lines.append(f"Model Answer: {item['model_answer']}")

        result = "\n".join(result_lines)

        st.download_button("📥 Download Result", result, file_name="Interview_Result.txt", mime="text/plain")

        if st.button("🔄 Restart Interview"):
            restart_interview()
            st.rerun()
