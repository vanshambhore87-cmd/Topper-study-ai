import streamlit as st
from google import genai
from google.genai.types import HttpOptions
import time
import os

# --- 1. SETUP & PERSISTENT MEMORY ---
st.set_page_config(page_title="Topper Study AI", page_icon="🎓", layout="wide")

def load_points():
    if not os.path.exists("points.txt"): return 0
    with open("points.txt", "r") as f: 
        content = f.read().strip()
        return int(content) if content else 0

def save_points(p):
    with open("points.txt", "w") as f: f.write(str(p))

api_key = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=api_key, http_options=HttpOptions(api_version="v1"))

if 'points' not in st.session_state:
    st.session_state.points = load_points()
if 'history' not in st.session_state:
    st.session_state.history = []
if 'daily_q' not in st.session_state:
    st.session_state.daily_q = None

# --- 2. RANK LOGIC ---
def get_rank(p):
    if p < 50: return "📖 Novice", 50
    if p < 250: return "🧠 Brainiac", 250
    if p < 600: return "🚀 Scholar", 600
    return "👑 Legendary Topper", 1000

current_rank, next_goal = get_rank(st.session_state.points)

# --- 3. SIDEBAR (The Hall of Fame & Rank) ---
with st.sidebar:
    st.title("🏆 Topper Dashboard")
    st.subheader(f"Rank: {current_rank}")
    st.metric("Your Points", st.session_state.points)
    
    st.progress(min(st.session_state.points / next_goal, 1.0))
    st.caption(f"Goal: {next_goal} for next Rank")
    
    st.divider()
    
    # NEW: Hall of Fame (Leaderboard)
    st.subheader("🥇 Hall of Fame")
    st.write(f"1. You ({current_rank}) — {st.session_state.points} pts")
    st.write("2. AI Scholar — 450 pts")
    st.write("3. Study King — 120 pts")

    st.divider()
    
    # Focus Timer (Now at the bottom so it's less intrusive)
    st.subheader("⏱️ Focus Timer")
    minutes = st.number_input("Minutes", min_value=1, value=25) 
    if st.button("Start Sprint"):
        with st.empty():
            for seconds in range(minutes * 60, 0, -1):
                # Using st.info so it's visible but out of the way
                st.info(f"🔥 Focus Mode! Time: {seconds // 60}:{seconds % 60:02d}")
                time.sleep(1)
            st.balloons()
            st.session_state.points += (minutes * 2)
            save_points(st.session_state.points)
            st.rerun()

# --- 4. MAIN INTERFACE ---
st.title("🚀 Smart Study Engine")
subject = st.selectbox("Choose Subject:", ["🟦 Physics", "🧪 Chemistry", "🧬 Biology", "📐 Maths", "🔤 English", "📜 History"])
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
                status.update(label="✅ Done! See ⬇️", state="complete")
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
            st.success("🎯 Correct!")
            st.balloons() 
            st.session_state.points += 50
            save_points(st.session_state.points)
            st.session_state.daily_q = None
            time.sleep(2) # Give time to see balloons before refresh
            st.rerun()
        else: st.error(f"Incorrect! It was {correct}")

# --- 6. HISTORY ---
if st.session_state.history:
    st.divider()
    with st.expander("📚 Your Notes History"):
        for item in st.session_state.history:
            st.write(f"📌 **{item['topic']}**")
