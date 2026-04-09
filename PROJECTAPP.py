import streamlit as st
from google import genai
from google.genai.types import HttpOptions
import time
import os

# --- 1. SETUP & PERSISTENT MEMORY ---
st.set_page_config(page_title="Topper Study AI", page_icon="🎓", layout="wide")

# This function saves/loads points from a hidden file so they don't reset
def load_points():
    if not os.path.exists("points.txt"): return 0
    with open("points.txt", "r") as f: return int(f.read())

def save_points(p):
    with open("points.txt", "w") as f: f.write(str(p))

api_key = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=api_key, http_options=HttpOptions(api_version="v1"))

if 'points' not in st.session_state:
    st.session_state.points = load_points() # Load saved points
if 'history' not in st.session_state:
    st.session_state.history = []
if 'daily_q' not in st.session_state:
    st.session_state.daily_q = None

# --- 2. RANK LOGIC ---
def get_rank(p):
    if p < 50: return "📖 Novice", 50
    if p < 250: return "🧠 Starter", 250
    if p < 600: return "🚀 Scholar", 600
    return "👑 Legendary Topper", 1000

current_rank, next_goal = get_rank(st.session_state.points)

# --- 3. SIDEBAR (The Leaderboard & Rank) ---
with st.sidebar:
    st.title("🏆 Topper Dashboard")
    st.subheader(f"Rank: {current_rank}")
    st.metric("Total Points", st.session_state.points)
    
    # Progress Bar
    progress = min(st.session_state.points / next_goal, 1.0)
    st.progress(progress)
    st.caption(f"Target: {next_goal} for next Rank")
    
    st.divider()
    
    # Anti-Cheat Focus Timer
    st.subheader("⏱️ Focus Timer")
    # min_value=1 prevents the 0-minute rank-up cheat!
    minutes = st.number_input("Minutes", min_value=1, value=25) 
    if st.button("Start Sprint"):
        with st.empty():
            for seconds in range(minutes * 60, 0, -1):
                st.write(f"⏳ {seconds // 60}:{seconds % 60:02d}")
                time.sleep(1)
            st.balloons()
            st.session_state.points += (minutes * 2) # Points based on time spent
            save_points(st.session_state.points) # Save to memory
            st.rerun()

# --- 4. MAIN INTERFACE ---
st.title("🚀 Smart Study Engine")
subject = st.selectbox("Choose Subject:", ["🟦 Physics", "🧪 Chemistry", "🧬 Biology", "📐 Maths", "🔤 English", "📜 History","🔥Something New"])
topic = st.text_input(f"What {subject} topic?", placeholder="e.g. Trigonometry")

if st.button("Finding best notes"):
    if topic:
        with st.status("🔍 Searching...", expanded=True) as status:
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash-lite", 
                    contents=f"Explain {topic} for 10th grade {subject}. Give 3 topper points and 1 tip."
                )
                st.markdown(response.text)
                st.session_state.history.append({"topic": topic, "notes": response.text})
                st.session_state.points += 5
                save_points(st.session_state.points)
                status.update(label="✅ Done!", state="complete")
            except: st.error("Busy!")

# --- 5. DYNAMIC DAILY CHALLENGE ---
st.divider()
st.subheader("📝 Daily Revision Challenge")
if st.button("Generate New Challenge"):
    with st.spinner("Creating..."):
        try:
            q_res = client.models.generate_content(model="gemini-2.5-flash-lite", contents="Give a 10th grade question with a one-word answer. Format: Q: [text] | A: [word]")
            if "|" in q_res.text:
                st.session_state.daily_q = [q_res.text.split("|")[0].replace("Q:","").strip(), q_res.text.split("|")[1].replace("A:","").strip()]
        except: st.error("Busy!")

if st.session_state.daily_q:
    st.info(f"Challenge: {st.session_state.daily_q[0]}")
    user_ans = st.text_input("Answer (One word):")
    if st.button("Check Answer"):
        correct = st.session_state.daily_q[1].lower().strip()
        user = user_ans.lower().strip()
        if user in correct or correct in user:
            st.balloons() # Balloons trigger BEFORE refresh
            time.sleep(1) # Small delay to see balloons
            st.session_state.points += 50
            save_points(st.session_state.points)
            st.session_state.daily_q = None
            st.rerun()
        else: st.error(f"Incorrect! It was {correct}")
