import streamlit as st
import requests
import random

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & K-POP AESTHETIC STYLING
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Celebs Scoop",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom Injection for Wine Red Background & Neon K-Pop Vibe Typography
st.markdown("""
    </style>
    /* Main container background */
    .stApp {
        background: linear-gradient(135deg, #4a000e 0%, #2b0004 50%, #120002 100%);
        color: #fff0f2;
        font-family: 'Segoe UI', Roboto, sans-serif;
    }
    
    /* Neon Pink/White Title Text (K-Pop Style Accent) */
    .kpop-title {
        font-size: 3rem !important;
        font-weight: 800;
        text-align: center;
        background: linear-gradient(45deg, #ff758f, #ffffff, #ff758f);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 15px rgba(255, 117, 143, 0.6);
        margin-bottom: 5px;
    }
    
    .kpop-subtitle {
        font-size: 1.4rem;
        font-style: italic;
        text-align: center;
        color: #ffb3c1;
        font-weight: 300;
        margin-bottom: 30px;
        letter-spacing: 1px;
    }
    
    /* Cards and Borders */
    .celebrity-card {
        background-color: rgba(255, 255, 255, 0.07);
        border: 1px solid rgba(255, 117, 143, 0.3);
        border-radius: 15px;
        padding: 20px;
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
    }
    
    /* Input Styling customization */
    div[data-baseweb="input"] {
        background-color: rgba(255, 255, 255, 0.1) !important;
        border-radius: 10px !important;
        border: 1px solid #ff758f !important;
    }
    input {
        color: white !important;
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(45deg, #c9184a, #ff758f) !important;
        color: white !important;
        border: none !important;
        border-radius: 20px !important;
        padding: 10px 25px !important;
        font-weight: bold !important;
        transition: all 0.3s ease;
        box-shadow: 0 0 10px rgba(201, 24, 74, 0.4);
    }
    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0 0 20px rgba(255, 117, 143, 0.8);
    }
    </style>
""", unsafe_allowed_html=True)

# -----------------------------------------------------------------------------
# 2. AUDIO STREAMING INITIALIZATION
# -----------------------------------------------------------------------------
AUDIO_URL = "https://audio.com/starstream/audio/jennie-blackpink-like-jennie/download"

# Hidden audio element to autoplay background music
st.markdown(f"""
    <audio autoplay loop muted style="display:none;">
        <source src="{AUDIO_URL}" type="audio/mpeg">
    </audio>
""", unsafe_allowed_html=True)

with st.expander("🎵 Background Music Track Controls"):
    st.audio(AUDIO_URL, format="audio/mp3", loop=True)

# -----------------------------------------------------------------------------
# 3. CORE HEADER LAYOUT
# -----------------------------------------------------------------------------
st.markdown('<div class="kpop-title">Celebs Scoop</div>', unsafe_allowed_html=True)
st.markdown('<div class="kpop-subtitle">Meet with the famous and fabulous celebs</div>', unsafe_allowed_html=True)

# -----------------------------------------------------------------------------
# 4. API UTILITY FUNCTIONS (WIKIPEDIA ENGINE)
# -----------------------------------------------------------------------------
def fetch_celebrity_data(query):
    if not query.strip():
        return None
        
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{query.replace(' ', '_')}"
    try:
        response = requests.get(url, headers={"User-Agent": "CelebScoopApp/1.0"})
        if response.status_code == 200:
            data = response.json()
            return {
                "name": data.get("title", query),
                "bio": data.get("extract", "No bio details found."),
                "image": data.get("originalimage", {}).get("source", "https://images.unsplash.com/photo-1549633030-89d0743bad01?w=500"),
                "description": data.get("description", "Global Icon")
            }
    except Exception:
        pass
    return None

def generate_quiz_question(celeb_name, bio_text):
    facts = [sentence.strip() for sentence in bio_text.split('.') if len(sentence.strip()) > 20]
    
    if len(facts) > 1:
        chosen_fact = facts[1] if len(facts) > 1 else facts[0]
        question = chosen_fact.replace(celeb_name, "_________").replace(celeb_name.lower(), "_________")
        wrong_answers = ["Lisa (BLACKPINK)", "Jennie", "Jungkook (BTS)", "Zendaya", "Timothée Chalamet", "G-Dragon", "Rihanna"]
        choices = [celeb_name] + random.sample([w for w in wrong_answers if w != celeb_name], 3)
        random.shuffle(choices)
        return {"question": f"Who is referred to in this context?\n\n\"{question}.\"", "answer": celeb_name, "choices": choices}
        
    choices = [celeb_name, "Jisoo", "V (BTS)", "Tom Holland"]
    random.shuffle(choices)
    return {
        "question": f"Which superstar matches the signature background profile of '{celeb_name}'?",
        "answer": celeb_name,
        "choices": choices
    }

# -----------------------------------------------------------------------------
# 5. STATE ENGINE
# -----------------------------------------------------------------------------
if "current_celeb" not in st.session_state:
    st.session_state.current_celeb = None
if "celeb_profile" not in st.session_state:
    st.session_state.celeb_profile = None
if "asked_questions" not in st.session_state:
    st.session_state.asked_questions = set()
if "quiz_data" not in st.session_state:
    st.session_state.quiz_data = None
if "score" not in st.session_state:
    st.session_state.score = 0

# -----------------------------------------------------------------------------
# 6. APPLICATION RUNTIME CONTROLLER
# -----------------------------------------------------------------------------
search_input = st.text_input("🔍 Search any Global or K-Pop Celebrity:", placeholder="e.g., Jennie, BTS, Billie Eilish...")

if search_input and search_input != st.session_state.current_celeb:
    profile = fetch_celebrity_data(search_input)
    if profile:
        st.session_state.celeb_profile = profile
        st.session_state.current_celeb = search_input
        st.session_state.quiz_data = generate_quiz_question(profile["name"], profile["bio"])
    else:
        st.error("Could not find database profiles matching that title. Try refining your spelling!")

if st.session_state.celeb_profile:
    prof = st.session_state.celeb_profile
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.image(prof["image"], use_column_width="always", caption=prof["description"])
        
    with col2:
        st.markdown(f"### ✨ {prof['name']}")
        st.write(prof["bio"])
        
    st.write("---")
    st.markdown("### 🏆 Live Trivia Arena (Unlimited & Non-Repeating)")
    
    if st.session_state.quiz_data:
        qz = st.session_state.quiz_data
        st.info(qz["question"])
        
        user_choice = st.radio(
            "Select your final answer choice:", 
            options=qz["choices"], 
            key=f"q_{prof['name']}_{len(st.session_state.asked_questions)}"
        )
        
        if st.button("Submit Verified Answer"):
            if user_choice == qz["answer"]:
                st.success("🎉 Correct choice! Fantastic hit!")
                st.session_state.score += 1
            else:
                st.error(f"❌ Close, but no! The correct profile matching answer was **{qz['answer']}**.")
            
            st.session_state.asked_questions.add(f"{prof['name']}_{qz['question'][:15]}")
            st.session_state.quiz_data = generate_quiz_question(prof["name"], prof["bio"])
            st.rerun()

    st.metric(label="✨ Total Correct Score Streak", value=st.session_state.score)
