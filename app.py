"""
AI Interview Preparation Assistant — single-file build.

Practice interview questions across CS Fundamentals + role-specific tracks,
filter by difficulty (Easy / Medium / Hard), get answers graded (Claude
and/or OpenAI GPT if API keys are configured, otherwise keyword-based),
track progress per topic across sessions, and view all registered users'
data from a password-protected Admin Panel — all backed by a local JSON
file (students_data.json, created next to this script).

Run with:  streamlit run app. 
"""

import csv
import io
import json
import os
import re
import time
from datetime import datetime

import streamlit as st

st.set_page_config(page_title="AI Interview Preparation Assistant", page_icon="🤖", layout="centered")


# ============================================================
# SECTION 1 — QUESTION BANK
# ============================================================

QUESTIONS = {
    "CS Fundamentals": [
        {"q": "What is an Array?", "difficulty": "Easy", "topic": "Arrays",
         "keywords": ["contiguous", "memory", "index", "same type", "fixed size", "collection"],
         "model_answer": "An array is a collection of elements of the same type stored in contiguous memory locations, accessed using an index."},
        {"q": "What is the Time Complexity of accessing an element in an Array?", "difficulty": "Medium", "topic": "Arrays",
         "keywords": ["o(1)", "constant time", "index", "direct access"],
         "model_answer": "Accessing an array element by index is O(1) — constant time — because the memory address can be calculated directly from the index."},
        {"q": "What is a Linked List?", "difficulty": "Easy", "topic": "Linked List",
         "keywords": ["nodes", "pointer", "sequential", "dynamic", "next"],
         "model_answer": "A linked list is a linear data structure made of nodes, where each node holds data and a pointer/reference to the next node."},
        {"q": "What is the difference between a Singly and Doubly Linked List?", "difficulty": "Medium", "topic": "Linked List",
         "keywords": ["single pointer", "next", "previous", "both directions", "traverse"],
         "model_answer": "A singly linked list has nodes pointing only to the next node, while a doubly linked list has nodes with pointers to both the next and previous nodes, allowing traversal in both directions."},
        {"q": "What is a Stack?", "difficulty": "Easy", "topic": "Stack",
         "keywords": ["lifo", "last in first out", "push", "pop", "top"],
         "model_answer": "A stack is a linear data structure that follows LIFO (Last In, First Out) order, with push and pop operations happening at the top."},
        {"q": "Where is a Stack used in real applications?", "difficulty": "Medium", "topic": "Stack",
         "keywords": ["call stack", "undo", "expression evaluation", "backtracking", "recursion"],
         "model_answer": "Stacks are used in function call stacks, undo/redo features, expression evaluation (like parentheses matching), and backtracking algorithms."},
        {"q": "What is a Queue?", "difficulty": "Easy", "topic": "Queue",
         "keywords": ["fifo", "first in first out", "enqueue", "dequeue", "front", "rear"],
         "model_answer": "A queue is a linear data structure that follows FIFO (First In, First Out) order, with elements added at the rear and removed from the front."},
        {"q": "What is the difference between a Queue and a Stack?", "difficulty": "Medium", "topic": "Queue",
         "keywords": ["fifo", "lifo", "order", "front", "top"],
         "model_answer": "A queue processes elements in FIFO order (first added, first removed), while a stack processes them in LIFO order (last added, first removed)."},
        {"q": "What is DBMS?", "difficulty": "Easy", "topic": "DBMS",
         "keywords": ["database management system", "store", "manage", "retrieve", "software"],
         "model_answer": "DBMS (Database Management System) is software that lets users create, store, manage, and retrieve data in a structured, efficient, and secure way."},
        {"q": "What is Normalization in DBMS?", "difficulty": "Medium", "topic": "DBMS",
         "keywords": ["redundancy", "organize", "tables", "dependency", "anomalies"],
         "model_answer": "Normalization is the process of organizing database tables to reduce data redundancy and avoid update/insert/delete anomalies, usually by splitting data across related tables."},
        {"q": "What is an Operating System?", "difficulty": "Easy", "topic": "OS",
         "keywords": ["software", "manages", "hardware", "resources", "interface"],
         "model_answer": "An operating system is system software that manages computer hardware and resources, and provides an interface between the user and the hardware."},
        {"q": "What is the difference between a Process and a Thread?", "difficulty": "Medium", "topic": "OS",
         "keywords": ["independent", "lightweight", "shared memory", "own memory", "execution"],
         "model_answer": "A process is an independent program in execution with its own memory space, while a thread is a lightweight unit within a process that shares the process's memory with other threads."},
        {"q": "How would you find the maximum subarray sum in an array?", "difficulty": "Hard", "topic": "Arrays",
         "keywords": ["kadane", "subarray", "running sum", "maximum", "o(n)"],
         "model_answer": "Kadane's Algorithm solves this in O(n): keep a running sum of the current subarray, resetting it to 0 whenever it goes negative, and track the maximum sum seen so far."},
        {"q": "How do you detect a cycle in a Linked List?", "difficulty": "Hard", "topic": "Linked List",
         "keywords": ["floyd", "slow", "fast", "pointer", "cycle"],
         "model_answer": "Floyd's Cycle Detection (slow/fast pointers) uses two pointers moving at different speeds through the list; if they ever meet, a cycle exists."},
        {"q": "How would you implement a Stack using two Queues?", "difficulty": "Hard", "topic": "Stack",
         "keywords": ["two queues", "enqueue", "dequeue", "reverse order", "rotate"],
         "model_answer": "Push by enqueuing into the main queue, then dequeue and re-enqueue every earlier element behind it so the newest item ends up at the front, keeping LIFO order using only queue operations."},
        {"q": "How would you implement a Queue using two Stacks?", "difficulty": "Hard", "topic": "Queue",
         "keywords": ["two stacks", "push", "pop", "reverse", "amortized"],
         "model_answer": "Use an 'in' stack for enqueue operations; when a dequeue is needed and the 'out' stack is empty, pop everything from 'in' and push it onto 'out', reversing the order so the oldest element is on top."},
        {"q": "What is a Deadlock in DBMS and how can it be prevented?", "difficulty": "Hard", "topic": "DBMS",
         "keywords": ["deadlock", "transactions", "locks", "prevention", "wait"],
         "model_answer": "A deadlock occurs when two or more transactions each hold a lock the other needs and wait indefinitely; it can be prevented with timeout limits, lock ordering, or deadlock-detection algorithms that abort one transaction."},
        {"q": "What is a Deadlock in an Operating System and what are its necessary conditions?", "difficulty": "Hard", "topic": "OS",
         "keywords": ["mutual exclusion", "hold and wait", "no preemption", "circular wait"],
         "model_answer": "An OS deadlock happens when processes wait forever for resources held by each other; it requires four conditions: mutual exclusion, hold-and-wait, no preemption, and circular wait."},
    ],
    "Python Developer": [
        {"q": "What is Python?", "difficulty": "Easy", "topic": "Python Basics",
         "keywords": ["interpreted", "high-level", "programming language", "object-oriented", "dynamically typed"],
         "model_answer": "Python is a high-level, interpreted, general-purpose programming language known for readability and dynamic typing."},
        {"q": "What is a List?", "difficulty": "Easy", "topic": "Data Structures",
         "keywords": ["ordered", "mutable", "collection", "index", "square brackets"],
         "model_answer": "A list is an ordered, mutable collection of items in Python, defined using square brackets, e.g. [1, 2, 3]."},
        {"q": "What is a Dictionary?", "difficulty": "Medium", "topic": "Data Structures",
         "keywords": ["key", "value", "pair", "unordered", "mutable", "curly braces"],
         "model_answer": "A dictionary is a mutable collection of key-value pairs in Python, defined using curly braces, e.g. {'key': 'value'}."},
        {"q": "What is the Global Interpreter Lock (GIL) in Python?", "difficulty": "Hard", "topic": "Python Basics",
         "keywords": ["gil", "one thread", "bytecode", "cpython", "concurrency"],
         "model_answer": "The GIL is a mutex in CPython that allows only one thread to execute Python bytecode at a time, which limits true parallelism for CPU-bound multi-threaded code."},
        {"q": "What is the difference between a Shallow Copy and a Deep Copy?", "difficulty": "Hard", "topic": "Data Structures",
         "keywords": ["shallow", "deep", "nested", "reference", "independent"],
         "model_answer": "A shallow copy duplicates the outer object but keeps references to the same nested objects, while a deep copy recursively duplicates every nested object so the copy is fully independent."},
    ],
    "Data Analyst": [
        {"q": "What is Data Analysis?", "difficulty": "Easy", "topic": "Data Analysis Fundamentals",
         "keywords": ["inspect", "clean", "transform", "model", "insights", "decision"],
         "model_answer": "Data analysis is the process of inspecting, cleaning, transforming, and modeling data to discover useful insights and support decision-making."},
        {"q": "What is Pandas?", "difficulty": "Easy", "topic": "Tools & Libraries",
         "keywords": ["library", "python", "dataframe", "data manipulation", "analysis"],
         "model_answer": "Pandas is a Python library used for data manipulation and analysis, built around the DataFrame data structure."},
        {"q": "What is Data Cleaning?", "difficulty": "Medium", "topic": "Data Analysis Fundamentals",
         "keywords": ["missing", "duplicate", "errors", "inconsistent", "correcting", "removing"],
         "model_answer": "Data cleaning is the process of detecting and correcting (or removing) missing, duplicate, or inconsistent data to improve data quality."},
        {"q": "What is the difference between a Type I and Type II error in hypothesis testing?", "difficulty": "Hard", "topic": "Data Analysis Fundamentals",
         "keywords": ["false positive", "false negative", "null hypothesis", "significance"],
         "model_answer": "A Type I error is a false positive — rejecting a true null hypothesis — while a Type II error is a false negative — failing to reject a false null hypothesis."},
        {"q": "How would you handle a dataset too large to fit into memory using Pandas?", "difficulty": "Hard", "topic": "Tools & Libraries",
         "keywords": ["chunksize", "chunks", "dtype", "memory", "dask", "batches"],
         "model_answer": "Read the data in chunks using `chunksize`, downcast column dtypes to reduce memory, or switch to a library like Dask that processes data out-of-core in batches."},
    ],
    "Web Developer": [
        {"q": "What is HTML?", "difficulty": "Easy", "topic": "Frontend Basics",
         "keywords": ["markup", "language", "structure", "webpage", "tags"],
         "model_answer": "HTML (HyperText Markup Language) is the standard markup language used to structure content on webpages using tags."},
        {"q": "What is CSS?", "difficulty": "Easy", "topic": "Frontend Basics",
         "keywords": ["style", "stylesheet", "design", "layout", "presentation"],
         "model_answer": "CSS (Cascading Style Sheets) is used to style and control the layout and presentation of HTML elements."},
        {"q": "What is JavaScript?", "difficulty": "Medium", "topic": "Scripting",
         "keywords": ["scripting", "programming language", "interactive", "dynamic", "browser"],
         "model_answer": "JavaScript is a scripting/programming language that adds interactivity and dynamic behavior to webpages, running in the browser."},
        {"q": "What is the CSS Box Model?", "difficulty": "Hard", "topic": "Frontend Basics",
         "keywords": ["content", "padding", "border", "margin", "layout"],
         "model_answer": "The CSS Box Model describes how every element is rendered as a box made up of content, padding, border, and margin layers, which together determine its total size and spacing."},
        {"q": "What is the difference between var, let, and const in JavaScript?", "difficulty": "Hard", "topic": "Scripting",
         "keywords": ["scope", "block", "function", "reassign", "hoisting"],
         "model_answer": "`var` is function-scoped and hoisted, `let` is block-scoped and reassignable, and `const` is block-scoped but cannot be reassigned after declaration."},
    ],
    "Java Developer": [
        {"q": "What is Java?", "difficulty": "Easy", "topic": "Java Basics",
         "keywords": ["object-oriented", "platform-independent", "programming language", "jvm", "compiled"],
         "model_answer": "Java is an object-oriented, platform-independent programming language that runs on the Java Virtual Machine (JVM)."},
        {"q": "What is a Class in Java?", "difficulty": "Easy", "topic": "OOP Concepts",
         "keywords": ["blueprint", "object", "template", "properties", "methods"],
         "model_answer": "A class is a blueprint/template for creating objects, defining their properties (fields) and behaviors (methods)."},
        {"q": "What is Inheritance?", "difficulty": "Medium", "topic": "OOP Concepts",
         "keywords": ["reuse", "parent", "child", "extends", "properties", "methods"],
         "model_answer": "Inheritance allows a child class to reuse and extend the properties and methods of a parent class using the 'extends' keyword."},
        {"q": "What is the difference between JDK, JRE, and JVM?", "difficulty": "Hard", "topic": "Java Basics",
         "keywords": ["development kit", "runtime environment", "virtual machine", "compile", "execute"],
         "model_answer": "JDK is the full development kit (includes compiler + tools), JRE is the runtime environment needed to run Java programs, and JVM is the virtual machine that actually executes the compiled bytecode."},
        {"q": "What is Polymorphism and how is it implemented in Java?", "difficulty": "Hard", "topic": "OOP Concepts",
         "keywords": ["overloading", "overriding", "many forms", "runtime", "compile time"],
         "model_answer": "Polymorphism lets an object take many forms; in Java it's implemented via method overloading (compile-time) and method overriding (runtime, through inheritance and dynamic dispatch)."},
    ],
    "SQL Developer": [
        {"q": "What is SQL?", "difficulty": "Easy", "topic": "SQL Basics",
         "keywords": ["structured query language", "database", "query", "manage", "relational"],
         "model_answer": "SQL (Structured Query Language) is used to query, manage, and manipulate data in relational databases."},
        {"q": "What is a Primary Key?", "difficulty": "Easy", "topic": "Database Design",
         "keywords": ["unique", "identifier", "row", "not null", "table"],
         "model_answer": "A primary key is a column (or set of columns) that uniquely identifies each row in a table and cannot be null."},
        {"q": "What is a JOIN?", "difficulty": "Medium", "topic": "Database Design",
         "keywords": ["combine", "tables", "related", "column", "rows"],
         "model_answer": "A JOIN combines rows from two or more tables based on a related column between them."},
        {"q": "What is the difference between WHERE and HAVING clauses?", "difficulty": "Hard", "topic": "SQL Basics",
         "keywords": ["filter rows", "filter groups", "group by", "aggregate"],
         "model_answer": "WHERE filters individual rows before grouping/aggregation happens, while HAVING filters groups after a GROUP BY, typically used with aggregate functions."},
        {"q": "What is Indexing in a database and how does it improve performance?", "difficulty": "Hard", "topic": "Database Design",
         "keywords": ["index", "lookup", "faster", "b-tree", "search"],
         "model_answer": "An index is a data structure (often a B-tree) built on one or more columns that lets the database find rows without scanning the whole table, dramatically speeding up lookups and searches at the cost of extra storage and slower writes."},
    ],
}

TIME_LIMIT_SECONDS = 30
DIFFICULTY_LEVELS = ["Easy", "Medium", "Hard"]


def all_roles():
    return list(QUESTIONS.keys())


def filter_by_difficulty(question_list, difficulty):
    """difficulty: one of DIFFICULTY_LEVELS, or 'All' to skip filtering."""
    if difficulty == "All":
        return question_list
    return [q for q in question_list if q["difficulty"] == difficulty]


def all_topics():
    """Unique, order-preserved list of every topic across every role."""
    seen = []
    for role_qs in QUESTIONS.values():
        for q in role_qs:
            if q["topic"] not in seen:
                seen.append(q["topic"])
    return seen


def total_question_count():
    return sum(len(v) for v in QUESTIONS.values())


def questions_for_role(role):
    return QUESTIONS.get(role, [])


# Lightweight rule-based study suggestions used by the AI Roadmap page
# when the Anthropic API isn't configured (or as a solid baseline even when it is).
TOPIC_RESOURCES = {
    "Python Basics": "Revisit Python syntax, data types, and control flow. Try writing 10 small scripts.",
    "Data Structures": "Practice implementing and using lists, dicts, sets, and tuples in small exercises.",
    "Data Analysis Fundamentals": "Work through a real dataset end-to-end: clean it, explore it, summarize findings.",
    "Tools & Libraries": "Do a hands-on Pandas tutorial — loading, filtering, grouping, and merging data.",
    "Frontend Basics": "Rebuild a simple webpage layout from scratch using only HTML and CSS.",
    "Scripting": "Build a small interactive widget (form validation, counter, to-do list) in vanilla JavaScript.",
    "Java Basics": "Review Java syntax and compile/run a few basic programs from the command line.",
    "OOP Concepts": "Practice designing 2-3 classes with inheritance and method overriding.",
    "SQL Basics": "Write 10 SELECT queries against a sample database, increasing in complexity.",
    "Database Design": "Practice designing normalized tables and writing JOINs across them.",
}


# ============================================================
# SECTION 2 — PERSISTENCE (JSON-file storage)
# ============================================================

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "students_data.json")

def _empty_student(name, email, branch, year, preferred_role):
    return {
        "name": name,
        "email": email,
        "branch": branch,
        "year": year,
        "preferred_role": preferred_role,
        "topic_scores": {},
        "attempts": [],
    }


def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def normalize_email(email):
    return email.strip().lower()


def get_student(email):
    data = load_data()
    return data.get(normalize_email(email))


def upsert_profile(name, email, branch, year, preferred_role):
    """Create or update a student's profile without touching their history."""
    data = load_data()
    key = normalize_email(email)
    if key in data:
        data[key]["name"] = name
        data[key]["branch"] = branch
        data[key]["year"] = year
        data[key]["preferred_role"] = preferred_role
    else:
        data[key] = _empty_student(name, email, branch, year, preferred_role)
    save_data(data)
    return data[key]


def record_attempt(email, role, mode, feedback_log):
    """
    Persist the results of a completed Interview / Skill Assessment run.
    feedback_log items are expected to include a 'topic' key.
    """
    data = load_data()
    key = normalize_email(email)
    if key not in data:
        return  # profile must exist first

    student = data[key]
    total_score = sum(item["points"] for item in feedback_log)
    total_possible = len(feedback_log) * 10

    for item in feedback_log:
        topic = item.get("topic", "General")
        bucket = student["topic_scores"].setdefault(topic, {"earned": 0, "possible": 0})
        bucket["earned"] += item["points"]
        bucket["possible"] += 10

    student["attempts"].append({
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "role": role,
        "mode": mode,
        "score": total_score,
        "possible": total_possible,
        "feedback_log": feedback_log,
    })

    save_data(data)


def global_stats():
    """Aggregate stats across every student, used on the Home page."""
    data = load_data()
    num_students = len(data)
    all_attempts = [a for s in data.values() for a in s.get("attempts", [])]
    if all_attempts:
        total_earned = sum(a["score"] for a in all_attempts)
        total_possible = sum(a["possible"] for a in all_attempts) or 1
        success_rate = round(100 * total_earned / total_possible)
    else:
        success_rate = 0
    return {
        "num_students": num_students,
        "num_attempts": len(all_attempts),
        "success_rate": success_rate,
    }


# ============================================================
# SECTION 3 — GRADING (Claude + OpenAI GPT, with keyword fallback)
# ============================================================

# ---------------- Claude setup ----------------
CLAUDE_AVAILABLE = False
claude_client = None
try:
    import anthropic
    _anthropic_key = st.secrets.get("ANTHROPIC_API_KEY", None)
    if _anthropic_key:
        claude_client = anthropic.Anthropic(api_key=_anthropic_key)
        CLAUDE_AVAILABLE = True
except Exception:
    CLAUDE_AVAILABLE = False

# ---------------- OpenAI GPT setup ----------------
GPT_AVAILABLE = False
gpt_client = None
GPT_MODEL = "gpt-4o-mini"
try:
    import openai
    _openai_key = st.secrets.get("OPENAI_API_KEY", None)
    if _openai_key:
        gpt_client = openai.OpenAI(api_key=_openai_key)
        GPT_MODEL = st.secrets.get("OPENAI_MODEL", GPT_MODEL)
        GPT_AVAILABLE = True
except Exception:
    GPT_AVAILABLE = False

# Kept for backwards compatibility with any code referencing the old name
AI_AVAILABLE = CLAUDE_AVAILABLE or GPT_AVAILABLE


def available_providers():
    """Returns the list of grading providers usable right now."""
    providers = ["Keyword"]
    if CLAUDE_AVAILABLE:
        providers.append("Claude")
    if GPT_AVAILABLE:
        providers.append("GPT")
    return providers


def keyword_check(user_answer, keywords):
    """Fallback grading: substring keyword matching."""
    stripped = user_answer.strip()
    if stripped == "":
        return "Blank", [], 0, "Please write an answer before checking it."

    answer_lower = stripped.lower()
    matched = [kw for kw in keywords if kw.lower() in answer_lower]
    ratio = len(matched) / len(keywords) if keywords else 0

    if ratio >= 0.4:
        return "✅ Correct", matched, 10, "Good answer! You covered the key points."
    elif len(matched) >= 1:
        return "🟡 Partially Correct", matched, 5, "You're on the right track, but try to include more detail."
    else:
        return "❌ Incorrect", matched, 0, "This answer misses the key points. Check the model answer below."


def _grading_prompt(question_text, user_answer, model_answer):
    return f"""You are grading a candidate's interview answer.

Question: {question_text}
Model/Reference Answer: {model_answer}
Candidate's Answer: {user_answer}

Grade the candidate's answer for correctness and completeness compared to the reference answer,
even if worded differently. Respond ONLY with valid JSON, no extra text, in this exact format:
{{"verdict": "Correct" or "Partial" or "Incorrect", "score": <0, 5, or 10>, "feedback": "<one short sentence of feedback>", "key_points_covered": ["point1", "point2"]}}"""


def _parse_grading_json(text):
    text = text.strip()
    text = re.sub(r"^```json|```$", "", text).strip()
    data = json.loads(text)

    verdict = data.get("verdict", "Incorrect")
    score = int(data.get("score", 0))
    feedback = data.get("feedback", "")
    points = data.get("key_points_covered", [])

    label_map = {"Correct": "✅ Correct", "Partial": "🟡 Partially Correct", "Incorrect": "❌ Incorrect"}
    label = label_map.get(verdict, "❌ Incorrect")
    return label, points, score, feedback


def claude_check_answer(question_text, user_answer, model_answer):
    """Semantic grading using Claude. Returns None on failure (caller falls back)."""
    stripped = user_answer.strip()
    if stripped == "":
        return "Blank", [], 0, "Please write an answer before checking it."
    try:
        response = claude_client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=300,
            messages=[{"role": "user", "content": _grading_prompt(question_text, stripped, model_answer)}]
        )
        return _parse_grading_json(response.content[0].text)
    except Exception:
        return None


def gpt_check_answer(question_text, user_answer, model_answer):
    """Semantic grading using OpenAI GPT. Returns None on failure (caller falls back)."""
    stripped = user_answer.strip()
    if stripped == "":
        return "Blank", [], 0, "Please write an answer before checking it."
    try:
        response = gpt_client.chat.completions.create(
            model=GPT_MODEL,
            max_tokens=300,
            messages=[{"role": "user", "content": _grading_prompt(question_text, stripped, model_answer)}],
        )
        return _parse_grading_json(response.choices[0].message.content)
    except Exception:
        return None


def grade_answer(question_text, user_answer, keywords, model_answer):
    """Routes to the selected AI provider (session_state.ai_provider), else keyword grading."""
    provider = st.session_state.get("ai_provider", "Keyword")

    if provider == "Claude" and CLAUDE_AVAILABLE:
        result = claude_check_answer(question_text, user_answer, model_answer)
        if result is not None:
            return result
    elif provider == "GPT" and GPT_AVAILABLE:
        result = gpt_check_answer(question_text, user_answer, model_answer)
        if result is not None:
            return result

    return keyword_check(user_answer, keywords)


def generate_roadmap_text(name, preferred_role, weak_topics):
    """
    Optional: use the currently selected AI provider to write a short
    personalized roadmap paragraph. Returns None if unavailable/fails, so
    the caller can fall back to the rule-based topic resource list.
    """
    provider = st.session_state.get("ai_provider", "Keyword")
    if provider not in ("Claude", "GPT") or not weak_topics:
        return None

    topics_str = ", ".join(weak_topics)
    prompt = (
        f"Write a short (3-4 sentence), encouraging study roadmap for {name}, "
        f"who is preparing for a {preferred_role} interview and is currently weak in: "
        f"{topics_str}. Be specific and motivating, no headers or bullet points, plain prose only."
    )

    try:
        if provider == "Claude" and CLAUDE_AVAILABLE:
            response = claude_client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content[0].text.strip()
        elif provider == "GPT" and GPT_AVAILABLE:
            response = gpt_client.chat.completions.create(
                model=GPT_MODEL,
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.choices[0].message.content.strip()
    except Exception:
        return None
    return None


# ============================================================
# SECTION 4 — PAGES
# ============================================================

# ------------------------------------------------------------------
# Shared helpers
# ------------------------------------------------------------------

def is_valid_email(email):
    pattern = r"^[\w\.\+\-]+@[\w\-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


def goto(page_name):
    st.session_state.page = page_name
    st.rerun()


def current_student():
    """Returns the logged-in student's saved record, or None."""
    email = st.session_state.get("student_email")
    if not email:
        return None
    return get_student(email)


def require_profile(page_label):
    """Call at the top of a page that needs a student profile. Returns the
    student record, or renders a prompt + returns None if there isn't one."""
    student = current_student()
    if student is None:
        st.warning(f"Please complete your Student Profile before using **{page_label}**.")
        if st.button("👤 Go to Student Profile"):
            goto("Student Profile")
        return None
    return student


def topic_score_table(student):
    """Returns list of dicts: topic, current (0-100), target (100)."""
    rows = []
    for topic in all_topics():
        bucket = student["topic_scores"].get(topic, {"earned": 0, "possible": 0})
        current = round(100 * bucket["earned"] / bucket["possible"]) if bucket["possible"] else 0
        rows.append({"Topic": topic, "Current Score": current, "Target Score": 100,
                     "Attempted": bucket["possible"] > 0})
    return rows


def readiness_from_rows(rows):
    attempted = [r["Current Score"] for r in rows if r["Attempted"]]
    if not attempted:
        return None, "Not enough data yet — complete a Skill Assessment or Interview to see your readiness."
    avg = round(sum(attempted) / len(attempted))
    if avg >= 80:
        label = "🎉 You are Interview Ready!"
    elif avg >= 50:
        label = "📈 You are improving, but still need practice."
    else:
        label = "🔴 You need more practice before your interview."
    return avg, label


# ------------------------------------------------------------------
# HOME
# ------------------------------------------------------------------

def page_home():
    stats = global_stats()

    col1, col2, col3 = st.columns(3)
    col1.metric("Students Practicing", f"{stats['num_students']}+" if stats['num_students'] else "0")
    col2.metric("Questions Available", f"{total_question_count()}+")
    col3.metric("Success Rate", f"{stats['success_rate']}%" if stats['num_attempts'] else "—")

    st.divider()
    st.subheader("🎯 What This System Can Do")

    cards = [
        ("📊 Skill Assessment", "Test yourself across multiple topics at once.", "Skill Assessment"),
        ("💡 Interview Questions", "Practice timed, role-specific interview questions.", "Interview Questions"),
        ("⚠️ Weak Topic Detection", "See exactly which topics need more work.", "Progress Tracker"),
        ("📈 Progress Tracking", "Track your score against a target for every topic.", "Progress Tracker"),
        ("🗺️ AI Learning Roadmap", "Get a personalized study plan based on your gaps.", "AI Roadmap"),
        ("🧭 AI Readiness Prediction", "See an overall readiness verdict before the real thing.", "Dashboard"),
    ]

    for i in range(0, len(cards), 2):
        c1, c2 = st.columns(2)

        for col, (title, desc, target_page) in zip((c1, c2), cards[i:i + 2]):
            with col:
                with st.container(border=True):
                    st.markdown(f"**{title}**")
                    st.caption(desc)

                    if st.button(
                        "Open →",
                        key=f"home_card_{target_page}_{i}"
                    ):
                        goto(target_page)

    st.divider()
    if current_student() is None:
        st.success("Start your preparation journey today 🚀")
        if st.button("👤 Set Up Student Profile", type="primary"):
            goto("Student Profile")
    else:
        st.success(f"Welcome back, {current_student()['name']}! 🚀")
        if st.button("📊 Go to Dashboard", type="primary"):
            goto("Dashboard")


# ------------------------------------------------------------------
# STUDENT PROFILE
# ------------------------------------------------------------------

def page_profile():
    st.subheader("👤 Student Profile")

    existing = current_student()
    name_default = existing["name"] if existing else ""
    email_default = existing["email"] if existing else ""
    branch_default = existing["branch"] if existing else "BTech"
    year_default = existing["year"] if existing else "1st Year"
    role_default = existing["preferred_role"] if existing else all_roles()[0]

    with st.form("profile_form"):
        name = st.text_input("Enter Your Name", value=name_default)
        email = st.text_input("Enter Your Email", value=email_default)
        role = st.selectbox("Preferred Role", all_roles(),
                             index=all_roles().index(role_default) if role_default in all_roles() else 0)
        branch = st.selectbox("Branch", ["BTech", "BCA", "MCA", "BSc IT", "MTech", "Other"],
                               index=["BTech", "BCA", "MCA", "BSc IT", "MTech", "Other"].index(branch_default)
                               if branch_default in ["BTech", "BCA", "MCA", "BSc IT", "MTech", "Other"] else 0)
        year = st.selectbox("Year", ["1st Year", "2nd Year", "3rd Year", "4th Year", "Graduated"],
                             index=["1st Year", "2nd Year", "3rd Year", "4th Year", "Graduated"].index(year_default)
                             if year_default in ["1st Year", "2nd Year", "3rd Year", "4th Year", "Graduated"] else 0)
        submitted = st.form_submit_button("💾 Save Profile", type="primary")

    if submitted:
        if name.strip() == "" or email.strip() == "":
            st.error("Please enter your Name and Email.")
        elif not is_valid_email(email):
            st.error("Please enter a valid email address.")
        else:
            upsert_profile(name.strip(), email.strip(), branch, year, role)
            st.session_state.student_email = email.strip()
            st.success("Profile saved!")
            st.rerun()

    if existing:
        st.divider()
        st.caption(f"Signed in as **{existing['name']}** ({existing['email']}) — attempts so far: "
                    f"{len(existing['attempts'])}")


# ------------------------------------------------------------------
# SKILL ASSESSMENT (quick, multi-topic, untimed)
# ------------------------------------------------------------------

def page_skill_assessment():
    student = require_profile("Skill Assessment")
    if student is None:
        return

    st.subheader("📊 Skill Assessment")
    st.caption("Pick one or more roles to pull questions from. Answers are graded immediately, no timer.")

    if not st.session_state.get("sa_active"):
        selected_roles = st.multiselect("Choose roles to be assessed on", all_roles(),
                                         default=[student["preferred_role"]])
        difficulty = st.selectbox("Difficulty", ["All"] + DIFFICULTY_LEVELS)

        question_list = []
        for r in selected_roles:
            question_list.extend(questions_for_role(r))
        question_list = filter_by_difficulty(question_list, difficulty)

        if selected_roles and not question_list:
            st.warning("No questions match that difficulty for the roles you picked. Try 'All' or a different role.")

        if st.button("🚀 Start Assessment", type="primary", disabled=not question_list):
            st.session_state.sa_active = True
            st.session_state.sa_role_label = " + ".join(selected_roles)
            st.session_state.sa_question_list = question_list
            st.session_state.sa_index = 0
            st.session_state.sa_feedback_log = []
            st.rerun()
        return

    question_list = st.session_state.sa_question_list
    idx = st.session_state.sa_index

    if idx < len(question_list):
        current_q = question_list[idx]
        st.progress(idx / len(question_list))
        st.write(f"**Q{idx + 1} of {len(question_list)}** · _{current_q['topic']}_ · {current_q['difficulty']}")
        st.write(current_q["q"])

        answer = st.text_area("Your Answer", key=f"sa_answer_{idx}")
        if st.button("✅ Submit Answer", key=f"sa_submit_{idx}"):
            label, matched, points, feedback = grade_answer(
                current_q["q"], answer, current_q["keywords"], current_q["model_answer"]
            )
            if label == "Blank":
                st.warning(feedback)
            else:
                st.session_state.sa_feedback_log.append({
                    "question": current_q["q"], "topic": current_q["topic"],
                    "answer": answer.strip(), "result": label, "matched_keywords": matched,
                    "points": points, "model_answer": current_q["model_answer"], "feedback": feedback,
                })
                st.session_state.sa_index += 1
                st.rerun()
    else:
        st.success("🎉 Assessment complete!")
        log = st.session_state.sa_feedback_log
        total = sum(item["points"] for item in log)
        st.metric("Score", f"{total} / {len(log) * 10}")

        record_attempt(student["email"], st.session_state.sa_role_label, "Skill Assessment", log)

        for item in log:
            with st.expander(f"{item['question']} — {item['result']} ({item['points']} pts)"):
                st.write(f"**Your Answer:** {item['answer'] or '_(blank)_'}")
                st.write(f"**Model Answer:** {item['model_answer']}")

        if st.button("🔄 Take Another Assessment"):
            for k in ("sa_active", "sa_role_label", "sa_question_list", "sa_index", "sa_feedback_log"):
                st.session_state.pop(k, None)
            st.rerun()


# ------------------------------------------------------------------
# INTERVIEW QUESTIONS (the original timed flow, now persisted)
# ------------------------------------------------------------------

def page_interview():
    student = require_profile("Interview Questions")
    if student is None:
        return

    st.subheader("💡 Interview Questions")

    if not st.session_state.get("iv_active"):
        role = st.selectbox("Select Job Role", all_roles(),
                             index=all_roles().index(student["preferred_role"]))
        difficulty = st.selectbox("Difficulty", ["All"] + DIFFICULTY_LEVELS)

        question_list = filter_by_difficulty(questions_for_role(role), difficulty)
        if not question_list:
            st.warning("No questions match that difficulty for this role. Try 'All' or a different difficulty.")

        if st.button("🎯 Start Interview", type="primary", disabled=not question_list):
            st.session_state.iv_active = True
            st.session_state.iv_role = role
            st.session_state.iv_question_list = question_list
            st.session_state.iv_question_no = 0
            st.session_state.iv_score = 0
            st.session_state.iv_feedback_log = []
            st.session_state.iv_question_start_time = time.time()
            st.rerun()
        return

    question_list = st.session_state.iv_question_list

    if st.session_state.iv_question_no < len(question_list):
        current_q = question_list[st.session_state.iv_question_no]

        if st.session_state.iv_question_start_time is None:
            st.session_state.iv_question_start_time = time.time()

        elapsed = time.time() - st.session_state.iv_question_start_time
        remaining = max(0, int(TIME_LIMIT_SECONDS - elapsed))

        st.header(f"Question {st.session_state.iv_question_no + 1} of {len(question_list)}")
        st.caption(f"Topic: {current_q['topic']} · Difficulty: {current_q['difficulty']}")
        st.progress(st.session_state.iv_question_no / len(question_list))
        st.write(current_q["q"])

        timer_col, _ = st.columns([1, 3])
        with timer_col:
            if remaining > 0:
                st.info(f"⏰ Time Left: {remaining}s")
            else:
                st.warning("⏰ Time's up! Please submit your answer.")

        answer = st.text_area("Write Your Answer", key=f"iv_answer_{st.session_state.iv_question_no}")

        col1, col2 = st.columns([1, 1])
        with col1:
            check_clicked = st.button("🔍 Check Answer")
        with col2:
            next_clicked = st.button("Next ➡️")

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

        if next_clicked:
            with st.spinner("Scoring your answer..."):
                label, matched, points, feedback = grade_answer(
                    current_q["q"], answer, current_q["keywords"], current_q["model_answer"]
                )
            if label == "Blank":
                st.warning("Please write an answer before continuing (0 marks given for blank answers).")

            st.session_state.iv_score += points
            st.session_state.iv_feedback_log.append({
                "question": current_q["q"], "topic": current_q["topic"],
                "answer": answer.strip(), "result": label, "matched_keywords": matched,
                "points": points, "model_answer": current_q["model_answer"], "feedback": feedback,
            })
            st.session_state.iv_question_no += 1
            st.session_state.iv_question_start_time = time.time()
            st.rerun()

    else:
        st.header("🎉 Interview Completed")
        st.success(f"Final Score : {st.session_state.iv_score}")

        progress = st.session_state.iv_score / (len(question_list) * 10)
        st.progress(min(progress, 1.0))

        record_attempt(student["email"], st.session_state.iv_role, "Interview",
                                st.session_state.iv_feedback_log)

        st.subheader("📋 Answer Review")
        for i, item in enumerate(st.session_state.iv_feedback_log, start=1):
            with st.expander(f"Q{i}: {item['question']} — {item['result']} ({item['points']} pts)"):
                st.write(f"**Your Answer:** {item['answer'] if item['answer'] else '_(blank)_'}")
                st.write(f"**Feedback:** {item.get('feedback', '')}")
                st.write(f"**Key Points Detected:** {', '.join(item['matched_keywords']) if item['matched_keywords'] else 'none'}")
                st.write(f"**Model Answer:** {item['model_answer']}")

        result_lines = [
            f"Candidate Name : {student['name']}",
            f"Email : {student['email']}",
            f"Role : {st.session_state.iv_role}",
            "",
            f"Final Score : {st.session_state.iv_score}",
            "",
            "Answer Review:",
        ]
        for i, item in enumerate(st.session_state.iv_feedback_log, start=1):
            result_lines.append(f"\nQ{i}: {item['question']}")
            result_lines.append(f"Your Answer: {item['answer'] if item['answer'] else '(blank)'}")
            result_lines.append(f"Result: {item['result']} ({item['points']} pts)")
            result_lines.append(f"Feedback: {item.get('feedback', '')}")
            result_lines.append(f"Model Answer: {item['model_answer']}")
        result = "\n".join(result_lines)

        st.download_button("📥 Download Result", result, file_name="Interview_Result.txt", mime="text/plain")

        if st.button("🔄 Restart Interview"):
            for k in ("iv_active", "iv_role", "iv_question_list", "iv_question_no", "iv_score",
                      "iv_feedback_log", "iv_question_start_time"):
                st.session_state.pop(k, None)
            st.rerun()


# ------------------------------------------------------------------
# PROGRESS TRACKER
# ------------------------------------------------------------------

def page_progress_tracker():
    student = require_profile("Progress Tracker")
    if student is None:
        return

    st.subheader("📈 Progress Tracker")

    rows = topic_score_table(student)
    st.dataframe(
        [{"Topic": r["Topic"], "Current Score": r["Current Score"], "Target Score": r["Target Score"]} for r in rows],
        use_container_width=True, hide_index=False,
    )

    st.subheader("🎯 Interview Readiness")
    avg, label = readiness_from_rows(rows)
    if avg is not None:
        st.progress(avg / 100)
        st.write(f"**{avg}% overall** — {label}")
    else:
        st.info(label)


# ------------------------------------------------------------------
# DASHBOARD
# ------------------------------------------------------------------

def page_dashboard():
    student = require_profile("Dashboard")
    if student is None:
        return

    st.subheader("📊 Dashboard")

    attempts = student["attempts"]
    rows = topic_score_table(student)
    attempted_rows = [r for r in rows if r["Attempted"]]

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Attempts", len(attempts))
    avg, _ = readiness_from_rows(rows)
    c2.metric("Overall Score", f"{avg}%" if avg is not None else "—")
    if attempted_rows:
        best = max(attempted_rows, key=lambda r: r["Current Score"])
        worst = min(attempted_rows, key=lambda r: r["Current Score"])
        c3.metric("Best Topic", best["Topic"])
    else:
        c3.metric("Best Topic", "—")

    if attempted_rows:
        st.bar_chart({r["Topic"]: r["Current Score"] for r in attempted_rows})
        st.caption(f"⚠️ Weakest topic: **{worst['Topic']}** ({worst['Current Score']}%)")

    if attempts:
        st.subheader("🕘 Recent Attempts")
        for a in reversed(attempts[-5:]):
            ts = a["timestamp"].replace("T", " ")
            st.write(f"- {ts} · **{a['role']}** ({a['mode']}) · {a['score']}/{a['possible']}")
    else:
        st.info("No attempts yet — try a Skill Assessment or Interview to populate your dashboard.")


# ------------------------------------------------------------------
# AI ROADMAP
# ------------------------------------------------------------------

def page_roadmap():
    student = require_profile("AI Roadmap")
    if student is None:
        return

    st.subheader("🗺️ AI Learning Roadmap")

    rows = topic_score_table(student)
    attempted_rows = [r for r in rows if r["Attempted"]]
    weak_topics = [r["Topic"] for r in rows if not r["Attempted"] or r["Current Score"] < 50]

    if not attempted_rows:
        st.info("Complete at least one Skill Assessment or Interview to unlock a personalized roadmap.")
        return

    if not weak_topics:
        st.success("🎉 No major weak spots detected — keep practicing to stay sharp!")
        return

    st.write(f"Based on your progress, here's a focused plan for **{student['name']}** "
             f"targeting a **{student['preferred_role']}** role:")

    ai_text = generate_roadmap_text(student["name"], student["preferred_role"], weak_topics)
    if ai_text:
        st.info(ai_text)
    elif not (CLAUDE_AVAILABLE or GPT_AVAILABLE):
        st.caption("🤖 Add `ANTHROPIC_API_KEY` or `OPENAI_API_KEY` in Streamlit secrets, and select it in the "
                   "sidebar, for an AI-personalized version of this roadmap.")

    st.subheader("Recommended Focus Areas")
    for topic in weak_topics:
        with st.container(border=True):
            st.markdown(f"**⚠️ {topic}**")
            st.write(TOPIC_RESOURCES.get(topic, "Practice more questions in this area."))


# ------------------------------------------------------------------
# ADMIN PANEL — view every registered user's data in one place
# ------------------------------------------------------------------

def page_admin():
    st.subheader("🔐 Admin Panel")

    if not st.session_state.get("admin_authenticated"):
        st.info("This page is restricted. Enter the admin password to continue.")
        pwd = st.text_input("Admin Password", type="password")
        if st.button("🔓 Login"):
            expected = st.secrets.get("ADMIN_PASSWORD", "13032006")
            if pwd == expected:
                st.session_state.admin_authenticated = True
                st.rerun()
            else:
                st.error("Incorrect password.")
        return

    data = load_data()
    if not data:
        st.info("No users have registered yet.")
        if st.button("🔒 Log Out of Admin"):
            st.session_state.admin_authenticated = False
            st.rerun()
        return

    st.success(f"👥 Total Registered Users: {len(data)}")

    rows = []
    for email, s in data.items():
        score_rows = topic_score_table(s)
        avg, _ = readiness_from_rows(score_rows)
        rows.append({
            "Name": s["name"],
            "Email": s["email"],
            "Branch": s["branch"],
            "Year": s["year"],
            "Preferred Role": s["preferred_role"],
            "Total Attempts": len(s["attempts"]),
            "Overall Score %": avg if avg is not None else "-",
            "Last Activity": s["attempts"][-1]["timestamp"].replace("T", " ") if s["attempts"] else "Never",
        })

    st.dataframe(rows, use_container_width=True, hide_index=True)

    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
    st.download_button("📥 Download All Users (CSV)", buf.getvalue(),
                        file_name="all_users_data.csv", mime="text/csv")

    st.divider()
    st.subheader("🔍 View Individual User Detail")
    emails = list(data.keys())
    selected_email = st.selectbox("Select a user", emails,
                                   format_func=lambda e: f"{data[e]['name']} ({e})")
    if selected_email:
        s = data[selected_email]
        st.write(f"**Name:** {s['name']}  \n**Email:** {s['email']}  \n**Branch:** {s['branch']}  \n"
                 f"**Year:** {s['year']}  \n**Preferred Role:** {s['preferred_role']}")

        if not s["attempts"]:
            st.caption("No attempts yet.")
        for a in reversed(s["attempts"]):
            ts = a["timestamp"].replace("T", " ")
            with st.expander(f"{ts} · {a['role']} ({a['mode']}) · {a['score']}/{a['possible']}"):
                for item in a["feedback_log"]:
                    st.write(f"- **{item['question']}** ({item['topic']}) → {item['result']} ({item['points']} pts)")

    st.divider()
    if st.button("🔒 Log Out of Admin"):
        st.session_state.admin_authenticated = False
        st.rerun()


# ============================================================
# SECTION 5 — APP ENTRY / NAVIGATION
# ============================================================



# ------------------- SESSION STATE DEFAULTS -------------------
_providers = available_providers()  # always includes "Keyword"; may include "Claude" / "GPT"
defaults = {
    "page": "Home",
    "student_email": None,
    "admin_authenticated": False,
    # Default to the best available AI grader, falling back to keyword matching
    "ai_provider": "Claude" if CLAUDE_AVAILABLE else ("GPT" if GPT_AVAILABLE else "Keyword"),
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

PAGES = {
    "Home": page_home,
    "Student Profile": page_profile,
    "Skill Assessment": page_skill_assessment,
    "Dashboard": page_dashboard,
    "AI Roadmap": page_roadmap,
    "Interview Questions": page_interview,
    "Progress Tracker": page_progress_tracker,
    "Admin Panel": page_admin,
}

# ------------------- SIDEBAR -------------------
with st.sidebar:
    st.title("🤖 AI Interview\nPreparation")
    st.caption("Navigation")
    choice = st.radio(
        "Navigation", list(PAGES.keys()),
        index=list(PAGES.keys()).index(st.session_state.page),
        label_visibility="collapsed",
    )
    if choice != st.session_state.page:
        st.session_state.page = choice
        st.rerun()

    student = current_student()
    st.divider()
    if student:
        st.success(f"👤 {student['name']}\n\n{student['preferred_role']}")
    else:
        st.info("No profile yet.")

    st.divider()
    st.caption("🤖 Answer Grading")
    if len(_providers) > 1:
        st.session_state.ai_provider = st.radio(
            "Grading method", _providers,
            index=_providers.index(st.session_state.ai_provider) if st.session_state.ai_provider in _providers else 0,
        )
        provider_labels = {"Claude": "Claude (semantic)", "GPT": "OpenAI GPT (semantic)", "Keyword": "Keyword matching"}
        st.caption(f"Using: **{provider_labels.get(st.session_state.ai_provider, st.session_state.ai_provider)}**")
    else:
        st.session_state.ai_provider = "Keyword"
        st.info("Using keyword-based checking.\n\n"
                 "Add `ANTHROPIC_API_KEY` and/or `OPENAI_API_KEY` in Streamlit secrets to unlock "
                 "AI-based semantic grading (Claude and/or GPT).")

# ------------------- MAIN CONTENT -------------------
st.title("🤖 AI Interview Preparation Assistant")

PAGES[st.session_state.page]()
