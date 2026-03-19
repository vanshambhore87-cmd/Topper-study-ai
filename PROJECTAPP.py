import streamlit as st
import time
from google import genai

# --- 1. NEW SDK CONFIGURATION ---
# Using the NEW Client structure
client = genai.Client(api_key="AIzaSyCizdZZMl5T83o74btHMExOlhDD3c64A1k")

# --- 2. PAGE SETUP ---
st.set_page_config(page_title="99.95% Study SaaS", page_icon="🎯")

# --- 3. MAIN INTERFACE ---
st.title("🚀 Smart Study Assistant")

topic = st.text_input("What topic are you stuck on?", placeholder="e.g. Ohm's Law")

if st.button("Explain for Board Exams"):
    if topic:
        with st.spinner("Talking to Gemini 2.5..."):
            try:
                # Using the newest model to avoid 404 errors
                response = client.models.generate_content(
                    model="gemini-2.5-flash", 
                    contents=f"Explain the 10th grade topic '{topic}' in 3 points for board exams."
                )
                st.success("Target Achieved!")
                st.write(response.text)
            except Exception as e:
                st.error(f"System Note: {e}")
                # Helping you understand the specific 429 quota error
                if "429" in str(e):
                    st.warning("Quota Limit Hit: Please link a billing account in Google Cloud Console to unlock the Free Tier.")
    else:
        st.warning("Please enter a topic.")

# --- 4. FOCUS TIMER ---
st.divider()
st.subheader("⏱️ Focus Timer")
mins = st.number_input("Minutes:", 1, 60, 25)
if st.button("Start Focusing"):
    bar = st.progress(0)
    for i in range(100):
        time.sleep(mins * 0.006) 
        bar.progress(i + 1)
    st.balloons()
