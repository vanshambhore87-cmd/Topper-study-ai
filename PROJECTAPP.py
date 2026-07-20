from google import genai
from google.genai.types import HttpOptions
import os
import time
import streamlit as st

# --- 1. PREMIUM SETUP & PERSISTENT MEMORY ---
st.set_page_config(
    page_title="Topper Study AI Pro", page_icon="💎", layout="wide"
)

# CSS FIX: Professional styling and dark text for metrics
st.markdown(
    """
    <style>
    .stButton>button { width: 100%; border-radius: 12px; height: 3em; background-color: #ff4b4b; color: white; font-weight: bold; border: none; }
    /* This fix makes metric text dark and visible regardless of theme */
    [data-testid="stMetricValue"] { color: #1f1f1f !important; font-weight: bold; }
    [data-testid="stMetricLabel"] { color: #555555 !important; font-size: 1rem !important; }
    .main { background-color: #f8f9fa; }
    </style>
    """,
    unsafe_allow_html=True,
)


def load_points():
  if not os.path.exists("points.txt"):
    return 0
  with open("points.txt", "r") as f:
    content = f.read().strip()
    return int(content) if content else 0


def save_points(p):
  with open("points.txt", "w") as f:
    f.write(str(p))


api_key = st.secrets["GEMINI_API_KEY"]
client = genai.Client(
    api_key=api_key, http_options=HttpOptions(api_version="v1")
)

if "points" not in st.session_state:
  st.session_state.points = load_points()
if "history" not in st.session_state:
  st.session_state.history = []
if "daily_q" not in st.session_state:
  st.session_state.daily_q = None


# --- 2. RANK LOGIC ---
def get_rank(p):
  if p < 50:
    return "📖 Novice", 50
  if p < 250:
    return "🧠 Brainiac", 250
  if p < 600:
    return "🚀 Scholar", 600
  return "👑 Legendary Topper", 1000


current_rank, next_goal = get_rank(st.session_state.points)

# --- 3. SIDEBAR (Clean & Honest) ---
with st.sidebar:
  st.title("🎓 Topper AI Pro")
  st.subheader(f"Rank: {current_rank}")

  # Using columns inside sidebar for better spacing
  m1, m2 = st.columns(2)
  m1.metric("Points", st.session_state.points)
  m2.metric("Goal", next_goal)

  st.progress(min(st.session_state.points / next_goal, 1.0))
  st.divider()

  st.subheader("📊 Your Progress")
  points_needed = next_goal - st.session_state.points
  if points_needed > 0:
    st.write(
        f"Keep going! **{points_needed}** points until you reach"
        f" **{get_rank(next_goal)[0]}**."
    )
  else:
    st.write("You've reached the top rank! 👑")

  st.divider()
  st.subheader("⏱️ Focus Timer")
  minutes = st.number_input("Minutes", 1, 120, 25)
  if st.button("🚀 Start Study Sprint"):
    with st.empty():
      for seconds in range(minutes * 60, 0, -1):
        st.info(f"⏳ Focus Mode: {seconds // 60}:{seconds % 60:02d}")
        time.sleep(1)
      st.balloons()
      st.session_state.points += minutes * 2
      save_points(st.session_state.points)
      st.rerun()

# --- 4. MAIN INTERFACE ---
st.title("🚀 Smart Study Engine")
left, right = st.columns([1, 1])

with left:
  st.subheader("🎯 Research Center")
  subject = st.selectbox(
      "Subject",
      ["Physics", "Chemistry", "Biology", "Maths", "English", "History", "Coding"],
  )
  topic = st.text_input("Topic to Master", placeholder="e.g. Cell Division")

  if st.button("✨ Get Topper Notes"):
    if topic:
      with st.status("🔍 Analyzing Database...") as s:
        try:
          res = client.models.generate_content(
              model="gemini-2.5-flash-lite",
              contents=(
                  f"Explain {topic} for 10th grade {subject}. Give 3 topper"
                  " points and 1 tip."
              ),
          )
          st.session_state.history.insert(
              0, {"topic": topic, "notes": res.text}
          )
          st.session_state.points += 5
          save_points(st.session_state.points)
          s.update(label="✅ Notes Ready!", state="complete")
        except:
          st.error("AI Busy. Try again in 10s.")

with right:
  st.subheader("📔 Output")
  if st.session_state.history:
    latest = st.session_state.history[0]
    st.info(f"Current Topic: {latest['topic']}")
    st.markdown(latest["notes"])
  else:
    st.write("Your notes will appear here!")

# --- 5. NEW FEATURE: INSTANT SHORT NOTES GENERATOR ---
st.divider()
st.subheader("📝 Short Notes Generator (10th Board Exam Ready)")
st.write(
    "Paste long textbook paragraphs, chapter text, or a complex topic to generate high-yield revision sheets!"
)

notes_input = st.text_area(
    "Paste Chapter / Topic Material Here:",
    height=160,
    placeholder="e.g., Paste Reflection & Refraction text, Chemical Reactions summary, or Biology notes...",
)

col_mode, col_btn = st.columns([2, 1])
with col_mode:
  detail_level = st.select_slider(
      "Select Revision Depth:",
      options=["Quick Revision (Bullet Points)", "Detailed Exam Summary"],
  )

with col_btn:
  st.write("")  # Spacing
  st.write("")
  gen_notes_btn = st.button("⚡ Generate Short Notes")

if gen_notes_btn:
  if notes_input.strip() == "":
    st.warning("Please paste some text or a topic first!")
  else:
    with st.spinner("Topper AI is distilling key exam points..."):
      try:
        notes_prompt = f"""
                You are a top 10th-grade exam tutor. Analyze the following text/topic and create structured Short Notes for exam preparation.
                
                Format the output strictly as:
                1. 📌 **Core Summary** (2-3 concise sentences)
                2. 🔑 **Key Terms & Definitions** (Bullet points)
                3. ⚡ **High-Yield Formulas / Laws / Core Rules**
                4. 🎯 **Top 3 Board Exam Style Questions** (with brief answers)
                
                Depth Level: {detail_level}
                
                Material to process:
                {notes_input}
                """
        res_notes = client.models.generate_content(
            model="gemini-2.5-flash-lite", contents=notes_prompt
        )

        st.success("Short Notes Generated! (+15 pts)")
        st.markdown(res_notes.text)

        # Save into history and add points
        st.session_state.history.insert(
            0, {"topic": "Short Notes Summary", "notes": res_notes.text}
        )
        st.session_state.points += 15
        save_points(st.session_state.points)
      except Exception as e:
        st.error("AI system busy. Please try again in a few seconds!")

# --- 6. VISION & CHALLENGE ---
st.divider()
col_v, col_c = st.columns(2)

with col_v:
  st.subheader("📸 Snap & Solve")
  img_file = st.file_uploader("Upload Question Image", type=["jpg", "png"])
  if img_file:
    st.image(img_file, width=250)
    if st.button("🧠 Solve Question"):
      with st.spinner("AI is reading..."):
        try:
          img_bytes = img_file.getvalue()
          response = client.models.generate_content(
              model="gemini-2.5-flash-lite",
              contents=[
                  "Solve this question step-by-step.",
                  {"mime_type": "image/jpeg", "data": img_bytes},
              ],
          )
          st.markdown(response.text)
          st.session_state.points += 10
          save_points(st.session_state.points)
        except:
          st.error("Image too blurry. Use better light!")

with col_c:
  st.subheader("📝 Daily Challenge")
  if st.button("🎲 Get New Question"):
    try:
      q_res = client.models.generate_content(
          model="gemini-2.5-flash-lite",
          contents="10th grade question. Format: Q: [text] | A: [word]",
      )
      if "|" in q_res.text:
        st.session_state.daily_q = [
            q_res.text.split("|")[0].replace("Q:", "").strip(),
            q_res.text.split("|")[1].replace("A:", "").strip(),
        ]
    except:
      st.error("Busy!")

  if st.session_state.daily_q:
    st.info(f"Q: {st.session_state.daily_q[0]}")
    user_ans = st.text_input("One-word Answer:")
    if st.button("🔥 Submit"):
      correct = st.session_state.daily_q[1].lower().strip()
      if (
          user_ans.lower().strip() in correct
          or correct in user_ans.lower().strip()
      ):
        st.success("🎯 Correct! +50 pts")
        st.balloons()
        st.session_state.points += 50
        save_points(st.session_state.points)
        st.session_state.daily_q = None
        time.sleep(1)
        st.rerun()
      else:
        st.error("Try again!")

# --- 7. HISTORY ---
if st.session_state.history:
  st.divider()
  with st.expander("📚 Your Session History"):
    for h in st.session_state.history:
      st.write(f"📌 **{h['topic']}**")
