# quiz_app.py
import base64
from pathlib import Path
import streamlit as st
from questions import questions
from utils import shuffle_options, check_answer

# ---------- PATHS ----------
BASE = Path(__file__).parent.resolve()
IMG_DIR = BASE / "assets" / "images"   # put cat.png here

def img_to_data_uri(path: Path) -> str:
    """Read an image file and return a base64 data URI (reliable on mobile/LAN)."""
    if not path.exists():
        return ""
    ext = path.suffix.lower().lstrip(".")
    mime = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png",
            "gif": "image/gif", "webp": "image/webp"}.get(ext, "image/png")
    b64 = base64.b64encode(path.read_bytes()).decode("utf-8")
    return f"data:{mime};base64,{b64}"

st.set_page_config(page_title="Katty's Quiz", page_icon="☕", layout="centered")

# ---------- THEME ----------
PALETTE = {
    "bg": "#3D2F1C",          # darker mocha background (nice on OLED)
    "panel": "#3D2F1C",
    "text": "#F3E9DF",        # light cocoa text
    "heading": "#F3D7BF",     # panna heading
    "accent": "#89B679",      # sage green
    "track": "rgba(243, 233, 223, 0.18)",
    "ring": "#6B4A2E",        # brown outline
    "btn": "#8B5E3C",
    "btn_text": "#FBF7F1",
    "option_bg": "rgba(243, 233, 223, 0.08)",
    "option_hover": "rgba(243, 233, 223, 0.16)",
}

# ---------- FONTS ----------
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Vollkorn:wght@400;700;800&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

# ---------- GLOBAL CSS ----------
st.markdown(f"""
<style>
:root {{ color-scheme: light; }}

[data-testid="stAppViewContainer"] > .main,
[data-testid="stAppViewContainer"] {{
  max-width: 420px;            /* iPhone 11 ~414px */
  margin: 0 auto;
  padding-left: 12px;
  padding-right: 12px;
  background: {PALETTE["bg"]};
}}
html, body, [class*="css"] {{
  color: {PALETTE["text"]};
  font-family: 'Vollkorn', Georgia, serif;
  -webkit-text-size-adjust: 100%;
}}

/* ===== Header row: avatar + title side-by-side ===== */
.header-row {{
  display:flex; align-items:center; gap:12px; width:100%;
}}
.header-row img {{
  margin-top: 16px; width:72px; height:auto; flex:0 0 auto; border-radius:12px;
}}
.header-row h1 {{
  margin:0; font-size:28px; line-height:1.1; color:{PALETTE["heading"]}; text-align:left;
}}

/* Counter + progress */
.small-muted {{
  text-align:center; color:{PALETTE["heading"]}; font-weight:700; margin:10px 0 6px 0; font-size:14px;
}}
.progress-wrap {{
  width:100%; height:16px; background:{PALETTE["track"]};
  border:2px solid {PALETTE["ring"]}; border-radius:999px; overflow:hidden;
}}
.progress-fill {{ height:100%; width:0%; background:{PALETTE["accent"]}; transition:width .35s ease; }}

/* Question */
.question {{ font-size:22px; font-weight:800; color:{PALETTE["heading"]}; margin:14px 0 10px 0; }}

/* Media helpers */
.qimg {{ width:100%; height:auto; display:block; border-radius:14px; }}
.qimg-bleed {{
  width:100vw; max-width:100vw; height:auto; display:block; border-radius:0;
  margin-left:calc(50% - 50vw); margin-right:calc(50% - 50vw);
}}

/* Radio cards */
div[role="radiogroup"] {{ width:100%; }}
div[role="radiogroup"] > label {{
  display:block; background:{PALETTE["option_bg"]}; color:{PALETTE["text"]};
  border:3px solid {PALETTE["ring"]}; border-radius:16px;
  padding:12px 12px 12px 46px; margin:10px auto; position:relative;
  font-size:18px; line-height:1.2; width:min(100%, 380px); box-sizing:border-box;
}}
div[role="radiogroup"] > label:hover {{ background:{PALETTE["option_hover"]}; cursor:pointer; }}

/* Hide the native radio bullet (keep accessible) */
div[role="radiogroup"] input[type="radio"] {{
  appearance:none; -webkit-appearance:none; -moz-appearance:none;
  opacity:0 !important; position:absolute !important; left:-9999px !important;
  width:0 !important; height:0 !important; margin:0 !important; padding:0 !important;
}}
/* Hide any SVG bullet some builds inject */
div[role="radiogroup"] label svg {{ display:none !important; width:0 !important; height:0 !important; overflow:hidden !important; }}

/* Our custom circle */
div[role="radiogroup"] > label::before {{
  content:""; position:absolute; left:14px; top:50%; transform:translateY(-50%);
  width:22px; height:22px; border-radius:50%;
  background:rgba(243,233,223,0.6); box-shadow:0 0 0 3px {PALETTE["ring"]} inset;
}}
div[role="radiogroup"] > label:has(input[type="radio"]:checked)::before {{
  background: radial-gradient(circle at center, #E7B977 45%, #E7B977 46%);
  box-shadow: 0 0 0 3px {PALETTE["ring"]} inset;
}}


/* Buttons */
div.stButton > button:first-child {{
  background:{PALETTE["btn"]}; color:{PALETTE["btn_text"]};
  border-radius:18px; border:3px solid {PALETTE["ring"]};
  font-size:18px; height:50px; width:min(100%, 380px); font-weight:700;
  display:block; margin:18px auto 0 auto;
}}
.stAlert > div {{ border-radius:14px; border:2px solid {PALETTE["ring"]}; }}
.block-container {{ padding-top:10px; padding-bottom:60px; }}
</style>
""", unsafe_allow_html=True)



# ---------- HEADER: avatar (cat.png) + title SIDE BY SIDE ----------
avatar_path = IMG_DIR / "cat.png"
if avatar_path.exists():
    avatar_uri = img_to_data_uri(avatar_path)
    st.markdown(f"""
    <div class="header-row">
      <img src="{avatar_uri}" alt="cat avatar" />
      <h1>Katty's Quiz</h1>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("<div class='header-row'><h1>Katty's Quiz</h1></div>", unsafe_allow_html=True)

# ---------- STATE ----------
if "current_q" not in st.session_state:
    st.session_state.current_q = 0
    st.session_state.score = 0
    st.session_state.finished = False
if "answered" not in st.session_state:
    st.session_state.answered = False
if "shuffled" not in st.session_state:
    st.session_state.shuffled_questions = shuffle_options(questions.copy())
    st.session_state.shuffled = True

total = len(questions)
idx = st.session_state.current_q
progress_pct = int((idx / max(total, 1)) * 100)

# ---------- COUNTER + PROGRESS ----------
st.markdown(
    f"<div class='small-muted'>Question {min(idx+1, total)}/{total}</div>",
    unsafe_allow_html=True,
)
st.markdown(
    f"<div class='progress-wrap'><div class='progress-fill' style='width:{progress_pct}%'></div></div>",
    unsafe_allow_html=True,
)

# ---------- QUIZ ----------
if not st.session_state.finished:
    q = st.session_state.shuffled_questions[idx]

    # Optional media per question (filenames relative to assets/images)
    if "image_full_bleed" in q:
        p = IMG_DIR / q["image_full_bleed"]
        if p.exists():
            st.markdown(f"<img src='{img_to_data_uri(p)}' class='qimg-bleed'/>", unsafe_allow_html=True)
        else:
            st.markdown(f"<img src='{q['image_full_bleed']}' class='qimg-bleed'/>", unsafe_allow_html=True)
    elif "image" in q:
        p = IMG_DIR / q["image"]
        if p.exists():
            st.markdown(f"<img src='{img_to_data_uri(p)}' class='qimg'/>", unsafe_allow_html=True)
        else:
            st.image(q["image"], use_column_width=True)

    if "audio" in q:
        ap = IMG_DIR / q["audio"]
        st.audio(str(ap if ap.exists() else q["audio"]))
    if "video" in q:
        vp = IMG_DIR / q["video"]
        st.video(str(vp if vp.exists() else q["video"]))

    # Question text
    st.markdown(f"<div class='question'>{q['question']}</div>", unsafe_allow_html=True)

    # Options
    choice = st.radio("Select your answer:", q["options"], key=f"q_{idx}", label_visibility="hidden")

    # Submit / Next
    if not st.session_state.answered:
        if st.button("Submit Answer"):
            if check_answer(choice, q["answer"]):
                st.success("✅ Correct!")
                st.session_state.score += 1
            else:
                st.error(f"❌ Wrong! Correct answer: {q['answer']}")
            st.session_state.answered = True
    else:
        if st.button("Next Question"):
            st.session_state.current_q += 1
            st.session_state.answered = False
            if st.session_state.current_q >= total:
                st.session_state.finished = True
            st.rerun()


# ---------- FINISH ----------
else:
    st.balloons()
    st.success(f" Bravo Kati! Score: {st.session_state.score}/{total}")
    end_gif = IMG_DIR / "end.gif"
    if end_gif.exists():
        st.markdown(f"<img src='{img_to_data_uri(end_gif)}' class='qimg'/>",
                    unsafe_allow_html=True)
    else:
        st.warning("Add your GIF at assets/images/end.gif to display it here.")

    if st.button("Restart Quiz"):
        st.session_state.current_q = 0
        st.session_state.score = 0
        st.session_state.finished = False
        st.rerun()
