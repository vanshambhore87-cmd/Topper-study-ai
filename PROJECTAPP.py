import streamlit as st
from google import genai
from google.genai.types import HttpOptions
import time

# --- 1. SETUP & STABLE CONFIG ---
st.set_page_config(page_title="Topper Study AI", page_icon="🎓", layout="wide")

# FIX: We force 'v1' to avoid the 404 Beta error seen in your screenshots
api_key = st.secrets["GEMINI_API_KEY"]
client = genai.Client(
    api_key=api_key, 
    http_options=HttpOptions(api_version="v1")
)

# Initialize points and history
if 'points' not in st.session_state:
    st.session_state.points = 0
if 'history' not in st.session_state:
    st.session_state.history = []

# --- 2. SIDEBAR (Dashboard & Timer) ---
with st.sidebar:
    st.title("🏆 Topper Dashboard")
    st.metric("Your Topper Points", st.session_state.points)
    
    st.divider()
    st.subheader("⏱️ Focus Timer")
    minutes = st.number_input("Set focus minutes", value=25)
    if st.button("Start Study Sprint"):
        with st.empty():
            for seconds in range(minutes * 60, 0, -1):
                st.write(f"⏳ Time Left: {seconds // 60}:{seconds % 60:02d}")
                time.sleep(1)
            st.balloons()
            st.session_state.points += 10
            st.success("Sprint Complete! +10 Points 🚀")

# --- 3. MAIN INTERFACE ---
st.title("🚀 Smart Study Engine")

# Colorful Subject Selection
subject = st.selectbox("Choose your Subject:", 
    ["🟦 Physics", "🧪 Chemistry", "🧬 Biology", "📐 Maths", "🔤 English", "📜 History"])

topic = st.text_input(f"What {subject} topic are you stuck on?", placeholder="e.g. Ohm's Law")

if st.button("Get Best Notes"):
    if topic:
        # Custom message: "Finding best notes" instead of "Asking AI"
        with st.status("🔍 Finding best notes and exam patterns...", expanded=True) as status:
            try:
                # Topper-specific prompt
                prompt = f"Explain {topic} for 10th grade {subject}. Give 3 mark-fetching points and 1 topper tip."
                
                # Requesting from the stable Gemini 1.5 Flash model
                response = client.models.generate_content(
                    model="gemini-1.5-flash", 
                    contents=prompt
                )
                
                status.update(label="✅ Notes Found!", state="complete")
                st.markdown(f"### 📔 Topper Notes: {topic}")
                st.write(response.text)
                
                # Save to History
                st.session_state.history.append({"topic": topic, "notes": response.text})
                
            except Exception as e:
                if "429" in str(e):
                    status.update(label="🚦 Traffic Jam!", state="error")
                    st.error("The AI is busy (Free Tier limit). Wait 20 seconds and click again!")
                else:
                    status.update(label="❌ Error", state="error")
                    st.error(f"Details: {e}")

# --- 4. DAILY REVISION TEST ---
st.divider()
st.subheader("📝 Daily Revision Challenge")
st.write("Question: What is the powerhouse of the cell? (Biology)")
answer = st.text_input("Your answer...")
if st.button("Submit Challenge"):
    if "mitochondria" in answer.lower():
        st.success("Correct! +20 Points 👑")
        st.session_state.points += 20
    else:
        st.error("Try again! Hint: It starts with 'M'.")

# --- 5. HISTORY SECTION ---
if st.session_state.history:
    st.divider()
    with st.expander("📚 Your Saved Notes (Session History)"):
        for item in st.session_state.history:
            st.write(f"📌 **{item['topic']}**")
