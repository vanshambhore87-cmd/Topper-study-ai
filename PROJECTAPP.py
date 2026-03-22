import streamlit as st
from google import genai
import time

# --- 1. SETUP ---
st.set_page_config(page_title="Topper Study AI", page_icon="🎓", layout="wide")

# Safe API Key
api_key = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=api_key)

# Initialize points and history in session memory
if 'points' not in st.session_state:
    st.session_state.points = 0
if 'history' not in st.session_state:
    st.session_state.history = []

# --- 2. SIDEBAR (Navigation & Timer) ---
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
    ["🟦 Physics", "🧪 Chemistry", "🧬 Biology", "📐 Maths", "📜 History/Civics","🔠English","🌍Geography"])

topic = st.text_input(f"What {subject} topic are you stuck on?", placeholder="e.g. Ohm's Law")

if st.button("Get Best Notes"):
    if topic:
        # Professional status bar
        with st.status("🔍 Finding best notes and exam patterns...", expanded=True) as status:
            try:
                # 1. Add a tiny pause to prevent "spamming" the API
                time.sleep(1) 
                
                # 2. The Topper Prompt
                topper_prompt = f"Explain {topic} for 10th grade {subject}. Give 3 mark-fetching points and 1 topper tip."
                
                # 3. Request the content
                response = client.models.generate_content(
                    model="gemini-1.5-flash-8b", 
                    contents=topper_prompt
                )
                
                # 4. Success!
                status.update(label="✅ Notes Found!", state="complete")
                st.markdown(f"### 📔 Topper Notes: {topic}")
                st.write(response.text)
                
                # Save to History
                st.session_state.history.append({"topic": topic, "notes": response.text})
                
            except Exception as e:
                # This catches the 429 error specifically
                if "429" in str(e):
                    status.update(label="🚦 please wait!", state="error")
                    st.error("The AI is a bit busy (Free Tier limit). Please wait 20 seconds and try again!")
                else:
                    status.update(label="❌ Error", state="error")
                    st.error(f"Something went wrong: {e}")

# --- 4. REVISION TEST (Daily Challenge) ---
st.divider()
st.subheader("📝 Daily Revision Challenge")
st.write("Question: Why is the sky blue? (Physics Challenge)")
answer = st.text_input("Your answer...")
if st.button("Submit Challenge"):
    if "scattering" in answer.lower():
        st.success("Correct! You understand Rayleigh Scattering! +20 Points")
        st.session_state.points += 20
    else:
        st.error("Close! Hint: Think about light scattering.")

# --- 5. HISTORY SECTION ---
if st.session_state.history:
    with st.expander("📚 Your Saved Notes (History)"):
        for item in st.session_state.history:
            st.write(f"**{item['topic']}**")
