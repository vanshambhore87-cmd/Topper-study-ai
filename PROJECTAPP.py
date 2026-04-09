
import streamlit as st
from google import genai
from google.genai.types import HttpOptions
import time

# --- 1. SETUP ---
st.set_page_config(page_title="Topper Study AI", page_icon="🎓", layout="wide")

api_key = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=api_key, http_options=HttpOptions(api_version="v1"))

# Initialize Session States
if 'points' not in st.session_state:
    st.session_state.points = 0
if 'history' not in st.session_state:
    st.session_state.history = []
if 'daily_q' not in st.session_state:
    st.session_state.daily_q = None

# --- 2. RANK LOGIC ---
def get_rank(p):
    if p < 50: return "📖 Novice", 50, "Blue"
    if p < 150: return "🧠 Starter", 150, "Green"
    if p < 300: return "🚀 Scholar", 300, "Orange"
    return "👑 Legendary Topper", 1000, "Gold"

current_rank, next_goal, color = get_rank(st.session_state.points)

# --- 3. SIDEBAR (The Leaderboard & Rank) ---
with st.sidebar:
    st.title("🏆 Topper Dashboard")
    
    # Rank Card
    st.subheader(f"Rank: {current_rank}")
    st.metric("Total Points", st.session_state.points)
    
    # Progress Bar
    progress = min(st.session_state.points / next_goal, 1.0)
    st.progress(progress)
    st.caption(f"{st.session_state.points} / {next_goal} to next Rank")
    
    st.divider()
    
    # Focus Timer
    st.subheader("⏱️ Focus Timer")
    minutes = st.number_input("Minutes", value=25)
    if st.button("Start Sprint"):
        with st.empty():
            for seconds in range(minutes * 60, 0, -1):
                st.write(f"⏳ {seconds // 60}:{seconds % 60:02d}")
                time.sleep(1)
            st.balloons()
            st.session_state.points += 20 # Timer now gives 20 points!
            st.rerun() # Refresh to update rank

# --- 4. MAIN INTERFACE ---
st.title("🚀 Smart Study Engine")

subject = st.selectbox("Choose Subject:", 
    ["🟦 Physics", "🧪 Chemistry", "🧬 Biology", "📐 Maths", "🔤 English", "📜 History", "🔥 Something New"])

topic = st.text_input(f"What {subject} topic?", placeholder="e.g. Trigonometry")

if st.button("Finding best notes"):
    if topic:
        with st.status("🔍 Searching topper database...", expanded=True) as status:
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash-lite", 
                    contents=f"Explain {topic} for 10th grade {subject}. Give 3 topper-style points and 1 secret tip."
                )
                status.update(label="✅ Notes Found!", state="complete")
                st.markdown(f"### 📔 Notes: {topic}")
                st.write(response.text)
                st.session_state.history.append({"topic": topic, "notes": response.text})
                st.session_state.points += 5 # Getting notes gives 5 points
            except Exception as e:
                st.error(f"Traffic Jam! (Error: {e})")

# --- 5. DYNAMIC DAILY CHALLENGE ---
st.divider()
st.subheader("📝 Daily Revision Challenge")

if st.button("Generate New Challenge"):
    with st.spinner("Creating..."):
        try:
            q_res = client.models.generate_content(
                model="gemini-2.5-flash-lite",
                contents=f"Give a 10th grade {subject} question with a one-word answer. Format: QUESTION: [text] | ANSWER: [word]"
            )
            raw = q_res.text
            if "|" in raw:
                st.session_state.daily_q = [raw.split("|")[0].replace("QUESTION:","").strip(), raw.split("|")[1].replace("ANSWER:","").strip()]
            else: st.warning("Try again!")
        except: st.error("Busy!")

if st.session_state.daily_q:
    st.info(f"Challenge: {st.session_state.daily_q[0]}")
    user_ans = st.text_input("Answer (One word):")
    if st.button("Check Answer"):
        correct = st.session_state.daily_q[1].lower().strip()
        user = user_ans.lower().strip()
        if user in correct or correct in user:
            st.success("🎯 +50 Points!")
            st.session_state.points += 50
            st.balloons()
            st.session_state.daily_q = None
            st.rerun() # Refresh to update Rank
        else:
            st.error(f"Incorrect! It was {correct}")

# --- 6. HISTORY ---
if st.session_state.history:
    st.divider()
    with st.expander("📚 Your Notes History"):
        for item in st.session_state.history:
            st.write(f"📌 **{item['topic']}**")
