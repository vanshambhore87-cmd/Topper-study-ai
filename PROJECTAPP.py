import streamlit as st
from google import genai
from google.genai.types import HttpOptions
import time
import os

# --- 1. PREMIUM SETUP & PERSISTENT MEMORY ---
st.set_page_config(page_title="Topper Study AI Pro", page_icon="💎", layout="wide")

# Styling to make it look like a high-end software business
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 20px; height: 3em; background-color: #ff4b4b; color: white; font-weight: bold; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

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

# --- 3. SIDEBAR (Professional Dashboard) ---
with st.sidebar:
    st.image("https://img.icons8.com/fluent/100/000000/education.png")
    st.title("Topper AI Pro")
    st.subheader(f"Rank: {current_rank}")
    
    col1, col2 = st.columns(2)
    col1.metric("Points", st.session_state.points)
    col2.metric("Goal", next_goal)
    
    st.progress(min(st.session_state.points / next_goal, 1.0))
    st.divider()
    
    st.subheader("🥇 Hall of Fame")
    st.write(f"1. You — {st.session_state.points} pts")
    st.write("2. AI Scholar — 450 pts")
    st.divider()
    
    st.subheader("⏱️ Focus Timer")
    minutes = st.number_input("Minutes", 1, 120, 25)
    if st.button("🚀 Start Sprint"):
        with st.empty():
            for seconds in range(minutes * 60, 0, -1):
                st.info(f"⏳ Focus Mode: {seconds // 60}:{seconds % 60:02d}")
                time.sleep(1)
            st.balloons()
            st.session_state.points += (minutes * 2)
            save_points(st.session_state.points)
            st.rerun()

# --- 4. MAIN ENGINE (Columns for clean UI) ---
st.title("🚀 Smart Study Engine")
left_col, right_col = st.columns([1, 1])

with left_col:
    st.subheader("🎯 Research Center")
    subject = st.selectbox("Subject", ["Physics", "Chemistry", "Biology", "Maths", "English", "History", "Coding"])
    topic = st.text_input("What are we mastering?", placeholder="e.g. Trigonometry")
    
    if st.button("✨ Generate Premium Notes"):
        if topic:
            with st.status("🔍 Searching topper database...") as s:
                try:
                    res = client.models.generate_content(
                        model="gemini-2.5-flash-lite", 
                        contents=f"Explain {topic} for 10th grade {subject}. Give 3 topper points and 1 tip."
                    )
                    st.session_state.history.insert(0, {"topic": topic, "notes": res.text})
                    st.session_state.points += 5
                    save_points(st.session_state.points)
                    s.update(label="✅ Analysis Complete!", state="complete")
                except: st.error("Traffic Jam! Wait 15s.")

with right_col:
    st.subheader("📔 Interactive Notebook")
    if st.session_state.history:
        latest = st.session_state.history[0]
        st.info(f"Topic: {latest['topic']}")
        st.markdown(latest['notes'])
    else:
        st.write("Generate notes to see them here!")

# --- 5. SNAP & SOLVE (The 'Rich App' Feature) ---
st.divider()
st.subheader("📸 Snap & Solve (Vision AI)")
c1, c2 = st.columns([1, 1])

with c1:
    source = st.radio("Source:", ["Camera", "Upload Image"], horizontal=True)
    img_file = st.camera_input("Scan Question") if source == "Camera" else st.file_uploader("Upload Photo", type=["jpg", "png"])

with c2:
    if img_file:
        st.image(img_file, width=300)
        if st.button("🧠 Analyze Image"):
            with st.spinner("AI is reading..."):
                try:
                    img_bytes = img_file.getvalue()
                    response = client.models.generate_content(
                        model="gemini-2.5-flash-lite",
                        contents=["Solve this 10th grade question step-by-step.", {"mime_type": "image/jpeg", "data": img_bytes}]
                    )
                    st.success("🎯 Solution Found!")
                    st.markdown(response.text)
                    st.session_state.points += 10
                    save_points(st.session_state.points)
                except: st.error("Could not read image. Try better lighting!")

# --- 6. DAILY CHALLENGE ---
st.divider()
st.subheader("📝 Daily Revision Challenge")
if st.button("🎲 Generate New Question"):
    try:
        q_res = client.models.generate_content(model="gemini-2.5-flash-lite", contents="10th grade question. Format: Q: [text] | A: [word]")
        if "|" in q_res.text:
            st.session_state.daily_q = [q_res.text.split("|")[0].replace("Q:","").strip(), q_res.text.split("|")[1].replace("A:","").strip()]
    except: st.error("Busy!")

if st.session_state.daily_q:
    st.info(f"Challenge: {st.session_state.daily_q[0]}")
    user_ans = st.text_input("Your Answer (One word):")
    if st.button("🔥 Check Answer"):
        correct = st.session_state.daily_q[1].lower().strip()
        if user_ans.lower().strip() in correct or correct in user_ans.lower().strip():
            st.success("🎯 Correct! +50 Points")
            st.balloons() 
            st.session_state.points += 50
            save_points(st.session_state.points)
            st.session_state.daily_q = None
            time.sleep(2)
            st.rerun()

# --- 7. HISTORY ---
if st.session_state.history:
    st.divider()
    with st.expander("📚 Your Session History"):
        for h in st.session_state.history:
            st.write(f"📌 **{h['topic']}**")
