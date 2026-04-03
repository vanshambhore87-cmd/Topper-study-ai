import streamlit as st
from google import genai
from google.genai.types import HttpOptions
import time

# --- 1. SETUP ---
st.set_page_config(page_title="Topper Study AI", page_icon="🎓", layout="wide")

# High-Stability Client Configuration
api_key = st.secrets["GEMINI_API_KEY"]
client = genai.Client(
    api_key=api_key,
    http_options=HttpOptions(api_version="v1") # Forces the stable production highway
)

# Initialize memory
if 'points' not in st.session_state:
    st.session_state.points = 0
if 'history' not in st.session_state:
    st.session_state.history = []

# --- 2. SIDEBAR ---
with st.sidebar:
    st.title("🏆 Topper Dashboard")
    st.metric("Topper Points", st.session_state.points)
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

topic = st.text_input(f"What {subject} topic are you stuck on?", placeholder="e.g. Gerund")

if st.button("Finding best notes"):
    if topic:
        with st.status("🔍 Searching topper database...", expanded=True) as status:
            # RETRY LOGIC: It will try up to 3 times if there is a Traffic Jam
            for attempt in range(3):
                try:
                    # Using '8b' for the HIGHEST free-tier request limits
                    response = client.models.generate_content(
                        model="gemini-1.5-flash-8b", 
                        contents=f"Explain {topic} for 10th grade {subject}. Give 3 topper-style points and 1 secret tip."
                    )
                    
                    status.update(label="✅ Notes Found!", state="complete")
                    st.markdown(f"### 📔 Notes: {topic}")
                    st.write(response.text)
                    st.session_state.history.append({"topic": topic, "notes": response.text})
                    break # Success! Exit the retry loop.
                
                except Exception as e:
                    if "429" in str(e) and attempt < 2:
                        status.write(f"🫨🚦😕 Traffic heavy... retrying in {attempt + 2}s...")
                        time.sleep(attempt + 2)
                    else:
                        status.update(label="❌ Connection Issue", state="error")
                        st.error(f"Google is very busy right now. Please wait 30 seconds and try again. Error: {e}")
                        break

# --- 4. HISTORY ---
if st.session_state.history:
    st.divider()
    with st.expander("📚 Your Saved Notes (Session History)"):
        for item in st.session_state.history:
            st.write(f"📌 **{item['topic']}**")

# --- 5. DAILY REVISION TEST ---
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
