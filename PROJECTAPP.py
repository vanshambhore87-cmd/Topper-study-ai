import streamlit as st
from google import genai
import time

# --- 1. SETUP ---
st.set_page_config(page_title="Topper Study AI", page_icon="🎓", layout="wide")

api_key = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=api_key)

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
    ["🟦 Physics", "🧪 Chemistry", "🧬 Biology", "📐 Maths", "🔤 English", "📜 History"])

topic = st.text_input(f"What {subject} topic?", placeholder="e.g. Trigonometry")

if st.button("Finding best notes"):
    if topic:
        with st.status("🔍 Searching topper database...", expanded=True) as status:
            try:
                response = client.models.generate_content(
                    model="gemini-2.0-flash", 
                    contents=f"Explain {topic} for 10th grade {subject}. Give 3 topper-style points and 1 secret tip."
                )
                status.update(label="✅ Notes Found!", state="complete")
                st.markdown(f"### 📔 Notes: {topic}")
                st.write(response.text)
                st.session_state.history.append({"topic": topic, "notes": response.text})
            except Exception as e:
                st.error(f"Traffic Jam! Wait 15 seconds. (Error: {e})")

# --- 4. NEW: DYNAMIC DAILY CHALLENGE ---
st.divider()
st.subheader("📝 Daily Revision Challenge")

if st.button("Generate New Challenge"):
    with st.spinner("Creating a challenge for you..."):
        try:
            q_res = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=f"Give one hard 10th grade {subject} question and its one-word answer. Format: Question | Answer"
            )
            st.session_state.daily_q = q_res.text.split("|")
        except:
            st.error("Too many requests! Wait a bit.")

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
    with st.expander("📚 Your Saved Notes"):
        for item in st.session_state.history:
            st.write(f"📌 **{item['topic']}**")
