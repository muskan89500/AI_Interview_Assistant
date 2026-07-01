
import streamlit as st
import time

# Page Configuration
st.set_page_config(page_title="AI Interview Preparation Assistant", page_icon="🤖")

# Title
st.title("🤖 AI Interview Preparation Assistant")
st.write("Welcome! Practice your interview skills.")

# Candidate Details
st.header("👤 Candidate Details")

name = st.text_input("Enter Your Name")
email = st.text_input("Enter Your Email")

role = st.selectbox(
    "Select Job Role",
    ["Python Developer", "Data Analyst", "Web Developer"]
)

# Questions

questions = {
    "Python Developer": [
        "What is Python?",
        "What is a List?",
        "What is a Dictionary?"
    ],


    "Data Analyst": [
        "What is Data Analysis?",
        "What is Pandas?",
        "What is Data Cleaning?"
    ],
    "Web Developer": [
        "What is HTML?",
        "What is CSS?",
        "What is JavaScript?"
    ]
}

# Start Interview


   # ------------------- START INTERVIEW -------------------

# Session State
if "start" not in st.session_state:
    st.session_state.start = False

if "question_no" not in st.session_state:
    st.session_state.question_no = 0

if "score" not in st.session_state:
    st.session_state.score = 0

# Start Button
if st.button("🎯 Start Interview"):
    st.session_state.start = True

# Interview Section
if st.session_state.start:

    if name == "" or email == "":
        st.error("Please enter your Name and Email.")

    else:

        st.success(f"Welcome {name}")
        st.write(f"**Role:** {role}")

        question_list = questions[role]

        # Show One Question
        if st.session_state.question_no < len(question_list):

            question = question_list[st.session_state.question_no]

            st.header(f"Question {st.session_state.question_no + 1}")
            st.write(question)

            st.info("⏰ Time Limit : 30 Seconds")

            answer = st.text_area(
                "Write Your Answer",
                key=f"answer_{st.session_state.question_no}"
            )

            if st.button("Next"):

                if len(answer.split()) >= 10:
                    st.session_state.score += 10
                else:
                    st.session_state.score += 5

                st.session_state.question_no += 1
                st.rerun()

        # Interview Completed
        else:

            st.header("🎉 Interview Completed")

            st.success(f"Final Score : {st.session_state.score}")

            progress = st.session_state.score / (len(question_list) * 10)
            st.progress(progress)

            result = f"""
Candidate Name : {name}
Email : {email}
Role : {role}

Final Score : {st.session_state.score}
"""

            st.download_button(
                "📥 Download Result",
                result,
                file_name="Interview_Result.txt",
                mime="text/plain"
            )