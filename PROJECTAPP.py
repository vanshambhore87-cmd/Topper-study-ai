import streamlit as st
from google import genai
import time

# --- 1. SETUP ---
st.set_page_config(page_title="Topper Study AI", page_icon="🎓", layout="wide")

# Simplified connection - let the library auto-detect the best stable route
api_key = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=api_key)

if 'points' not in st.session_state:
    st.session_state.points = 0
if 'history' not in st.session_state:
    st.session_state.history = []

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

topic = st.text_input(f"What {subject} topic?", placeholder="e.g. Gerund")

if st.button("Finding best notes"):
    if topic:
        with st.status("🔍 Searching topper database...", expanded=True) as status:
            try:
                # FIX: Using Gemini 2.5 Flash - The stablest model in 2026
                response = client.models.generate_content(
                    model="gemini-2.5-flash", 
                    contents=f"Explain {topic} for 10th grade {subject}. Give 3 topper-style points and 1 secret tip."
                )
                
                status.update(label="✅ Notes Found!", state="complete")
                st.markdown(f"### 📔 Notes: {topic}")
                st.write(response.text)
                st.session_state.history.append({"topic": topic, "notes": response.text})
                
            except Exception as e:
                # This specifically catches the 'Traffic Jam' speed limit
                if "429" in str(e):
                    status.update(label="🚦 Traffic Jam!", state="error")
                    st.error("Google's free highway is full. Wait 20 seconds and click again!")
                else:
                    status.update(label="❌ Connection Issue", state="error")
                    st.error(f"Try again in 30 seconds. (Details: {e})")

# --- 4. HISTORY ---
if st.session_state.history:
    st.divider()
    with st.expander("📚 Your Saved Notes"):
        for item in st.session_state.history:
            st.write(f"📌 **{item['topic']}**")
