import streamlit as st
from google import genai
import time

# --- 1. SETUP ---
st.set_page_config(page_title="Topper Study AI", page_icon="🎓", layout="wide")

# Simplified connection - let the library handle the version automatically
api_key = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=api_key)

# Initialize points and history
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

subject = st.selectbox("Choose your Subject:", 
    ["🟦 Physics", "🧪 Chemistry", "🧬 Biology", "📐 Maths", "🔤 English", "📜 History"])

topic = st.text_input(f"What {subject} topic are you stuck on?", placeholder="e.g. Ohm's Law")

if st.button("Get Best Notes"):
    if topic:
        with st.status("🔍 Finding best notes...", expanded=True) as status:
            try:
                # Force the model string to be exactly what Google's 'Stable' tier wants
                response = client.models.generate_content(
                    model="gemini-2.0-flash", 
                    contents=f"Explain {topic} for 10th grade {subject}. Give 3 mark-fetching points and 1 topper tip."
                )
                
                status.update(label="✅ Notes Found!", state="complete")
                st.markdown(f"### 📔 Topper Notes: {topic}")
                st.write(response.text)
                
                # Save to history
                st.session_state.history.append({"topic": topic, "notes": response.text})
                
            except Exception as e:
                # Catching and explaining the 429/404 errors clearly
                if "429" in str(e):
                    status.update(label="🚦 Traffic Jam!", state="error")
                    st.error("AI is busy (Free Tier limit). Please wait 20 seconds and try again.")
                elif "404" in str(e):
                    status.update(label="❌ Model Error", state="error")
                    st.error("Model version mismatch. Please contact support or try again in a few minutes.")
                else:
                    status.update(label="❌ Error", state="error")
                    st.error(f"Something went wrong: {e}")

# --- 4. HISTORY ---
if st.session_state.history:
    st.divider()
    with st.expander("📚 Your Saved Notes"):
        for item in st.session_state.history:
            st.write(f"**{item['topic']}**")
