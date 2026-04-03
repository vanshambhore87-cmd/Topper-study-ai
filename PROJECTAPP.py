import streamlit as st
from google import genai
import time

# --- 1. SETUP ---
st.set_page_config(page_title="Topper Study AI", page_icon="🎓", layout="wide")

# Simplified connection
api_key = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=api_key)

# Initialize memory
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
                # 1. We add a tiny delay to stay under the radar
                time.sleep(1.5) 
                
                # 2. We use the '8b' model which has higher free limits
                response = client.models.generate_content(
                    model="gemini-1.5-flash-8b", 
                    contents=f"Explain {topic} for 10th grade {subject}. Use bullet points and 1 topper tip."
                )
                
                status.update(label="✅ Notes Found!", state="complete")
                st.markdown(f"### 📔 Topper Notes: {topic}")
                st.write(response.text)
                
                # Save to history
                st.session_state.history.append({"topic": topic, "notes": response.text})
                
            except Exception as e:
                if "429" in str(e):
                    status.update(label="🚦 Traffic Jam!", state="error")
                    st.error("The AI is taking a breather. Wait 20 seconds and click again!")
                else:
                    status.update(label="❌ Error", state="error")
                    st.error(f"Something went wrong: {e}")

# --- 4. HISTORY ---
if st.session_state.history:
    st.divider()
    with st.expander("📚 Your Saved Notes"):
        for item in st.session_state.history:
            st.write(f"**{item['topic']}**")
