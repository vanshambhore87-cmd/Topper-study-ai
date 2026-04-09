import streamlit as st
from google import genai
from google.genai.types import HttpOptions  # Added this missing import
import time

# --- 1. SETUP ---
st.set_page_config(page_title="Topper Study AI", page_icon="🎓", layout="wide")

api_key = st.secrets["GEMINI_API_KEY"]

# Corrected Client Setup with HttpOptions
client = genai.Client(
    api_key=api_key, 
    http_options=HttpOptions(api_version="v1")
)

# Initialize Session States
if 'points' not in st.session_state:
    st.session_state.points = 0
if 'history' not in st.session_state:
    st.session_state.history = []
if 'daily_q' not in st.session_state:
    st.session_state.daily_q = None

# --- 2. SIDEBAR ---
with st.sidebar:
    st.title("🏆 Topper Dashboard")
    st.metric("Your Topper Points", st.session_state.points)
    st.divider()
    st.subheader("⏱️ Focus Timer")
    minutes = st.number_input("Minutes", value=25)
    if st.button("Start Sprint"):
        with st.empty():
            for seconds in range(minutes * 60, 0, -1):
                st.write(f"⏳ {seconds // 60}:{seconds % 60:02d}")
                time.sleep(1)
            st.balloons()
            st.session_state.points += 10

# --- 3. MAIN INTERFACE ---
st.title("🚀 Smart Study Engine")

subject = st.selectbox("Choose Subject:", 
    ["🟦 Physics", "🧪 Chemistry", "🧬 Biology", "📐 Maths", "🔤 English", "📜 History", "🔥 Something New"])

topic = st.text_input(f"What {subject} topic?", placeholder="e.g. Trigonometry")

if st.button("Finding best notes"):
    if topic:
        with st.status("🔍 Searching topper database...", expanded=True) as status:
            try:
                # Using the stablest 2026 model
                response = client.models.generate_content(
                    model="gemini-2.5-flash-lite", 
                    contents=f"Explain {topic} for 10th grade {subject}. Give 3 topper-style points and 1 secret tip."
                )
                status.update(label="✅ Notes Found!", state="complete")
                st.markdown(f"### 📔 Notes: {topic}")
                st.write(response.text)
                st.session_state.history.append({"topic": topic, "notes": response.text})
            except Exception as e:
                st.error(f"Traffic Jam! Wait 15 seconds. (Error: {e})")

# --- 4. DYNAMIC DAILY CHALLENGE ---
st.divider()
st.subheader("📝 Daily Revision Challenge")

if st.button("Generate New Challenge"):
    with st.spinner("Creating a challenge for you..."):
        try:
            # Updated to use the lite model to avoid 'limit 0' errors
            q_res = client.models.generate_content(
                model="gemini-2.5-flash-lite",
                contents=f"Give one hard 10th grade {subject} question and its one-word answer. Format: Question | Answer"
            )
            if "|" in q_res.text:
                st.session_state.daily_q = q_res.text.split("|")
            else:
                st.warning("The AI gave a weird format. Try generating again!")
        except Exception as e:
            st.error("Google is busy! Please wait a few seconds.")

if st.session_state.daily_q:
    st.info(f"Today's {subject} Challenge: {st.session_state.daily_q[0]}")
    user_ans = st.text_input("Your Answer (One word):")
    if st.button("Check Answer"):
        correct_ans = st.session_state.daily_q[1].strip().lower()
        if user_ans.lower() in correct_ans:
            st.success("🎯 Correct! You're a Genius! +50 Points")
            st.session_state.points += 50
            st.balloons()
            st.session_state.daily_q = None # Reset after win
        else:
            st.error(f"Wrong! The answer was {correct_ans}. Try a new one!")

# --- 5. HISTORY ---
if st.session_state.history:
    st.divider()
    with st.expander("📚 Your Notes History"):
        for item in st.session_state.history:
            st.write(f"📌 **{item['topic']}**")
