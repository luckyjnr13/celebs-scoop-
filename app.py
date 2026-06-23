import streamlit as st
import requests, random, base64
from datetime import datetime
import urllib.parse

st.set_page_config(page_title="Celeb Scoop 🎬", page_icon="✨", layout="wide")

NEWSAPI_KEY = st.secrets.get("NEWSAPI_KEY", "")

# ---------- Background + CSS ----------
def set_bg():
    bg_file = "assets/bg.jpg"
    try:
        with open(bg_file, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        css = f"""
        <style>
    .stApp {{
            background-image: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.8)),
            url("data:image/jpg;base64,{b64}");
            background-size: cover;
            background-attachment: fixed;
        }}
    .glass {{
            background: rgba(255,255,255,0.08);
            backdrop-filter: blur(12px);
            border-radius: 20px;
            padding: 1.5rem;
            border: 1px solid rgba(255,255,255,0.2);
            color: white;
        }}
        h1, h2, h3, p, label {{color: white!important;}}
        div.stButton > button {{
            background: linear-gradient(90deg,#ff0080,#ff8c00);
            color: white; border: none; border-radius: 12px;
            font-weight: 700; padding: 0.7rem 1.2rem; width: 100%;
        }}
        div.stButton > button:hover {{filter: brightness(1.15); transform: scale(1.02);}}
        </style>
        """
        st.markdown(css, unsafe_allow_html=True)
    except:
        st.markdown("<style>body{background:#0e1117;color:white}</style>", unsafe_allow_html=True)

set_bg()

def music_player():
    try:
        with open("assets/theme.mp3", "rb") as f:
            data = f.read()
        b64 = base64.b64encode(data).decode()
        st.audio(f"data:audio/mp3;base64,{b64}", format="audio/mp3", loop=True)
    except:
        st.caption("Add assets/theme.mp3 for background music")

# ---------- API Helpers ----------
@st.cache_data(ttl=300)
def get_news(celeb):
    if not NEWSAPI_KEY:
        return [{"title":f"{celeb} spotted at award show", "url":"#", "source":"Demo"}]
    url = f"https://newsapi.org/v2/everything?q={urllib.parse.quote(celeb)}&sortBy=publishedAt&language=en&pageSize=6&apiKey={NEWSAPI_KEY}"
    try:
        r = requests.get(url, timeout=8).json()
        return [{"title":a["title"], "url":a["url"], "source":a["source"]["name"]} for a in r.get("articles",[])]
    except:
        return []

@st.cache_data(ttl=3600)
def get_wikipedia_bio(celeb):
    """Try exact name, then search fallback"""
    # try direct page
    query = urllib.parse.quote(celeb.replace(" ", "_"))
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{query}"
    r = requests.get(url, timeout=8)
    if r.status_code == 200:
        data = r.json()
        if data.get("type")!= "disambiguation":
            return {
                "name": data.get("title", celeb),
                "bio": data.get("description", "Public figure"),
                "summary": data.get("extract", ""),
                "img": data.get("thumbnail", {}).get("source", ""),
                "url": data.get("content_urls", {}).get("desktop", {}).get("page", f"https://en.wikipedia.org/wiki/{query}")
            }
    # fallback: search API
    search_url = f"https://en.wikipedia.org/w/api.php?action=opensearch&search={urllib.parse.quote(celeb)}&limit=1&namespace=0&format=json"
    try:
        s = requests.get(search_url, timeout=8).json()
        if len(s[1]) > 0:
            title = s[1][0]
            return get_wikipedia_bio(title) # recurse with exact title
    except:
        pass
    return {"name": celeb, "bio": "Public figure", "summary": "No summary found. Try full name or different spelling.", "img": "", "url": f"https://en.wikipedia.org/wiki/{query}"}

def generate_quiz(celeb, news, bio):
    base_qs = [
        {"q": f"What is {celeb} best known as?", "opts": [bio["bio"], "Chef", "Astronaut", "Farmer"], "a": bio["bio"]},
        {"q": f"Which category fits {celeb}?", "opts": ["Entertainment", "Construction", "Mining", "Agriculture"], "a": "Entertainment"},
        {"q": f"Is {celeb} trending this week?", "opts": ["Yes", "No", "Maybe", "Unknown"], "a": "Yes"}
    ]
    if news:
        source = news[0]["source"]
        base_qs.append({"q": f"Latest news about {celeb} is from:", "opts": [source, "NASA", "WHO", "FIFA"], "a": source})
    for q in base_qs:
        random.shuffle(q["opts"])
    return base_qs

# ---------- Session State ----------
if "quiz_data" not in st.session_state:
    st.session_state.quiz_data = None
if "quiz_answers" not in st.session_state:
    st.session_state.quiz_answers = {}
if "last_celeb" not in st.session_state:
    st.session_state.last_celeb = ""

st.title("✨ Celeb Scoop")
st.caption("Type any celebrity → get Wikipedia bio + trending news + quiz. Only 1 API key needed.")
music_player()

col1, col2 = st.columns([2,1])
with col1:
    celeb = st.text_input("🔍 Search Celebrity", placeholder="e.g. Beyonce, Burna Boy, Zendaya, Davido")
    search_btn = st.button("Scoop It!")
with col2:
    st.metric("Last Updated", datetime.now().strftime("%H:%M:%S"))

if search_btn and celeb.strip():
    st.session_state.last_celeb = celeb.strip()
    with st.spinner(f"Scooping {celeb}..."):
        news = get_news(celeb)
        bio = get_wikipedia_bio(celeb)
        quiz = generate_quiz(celeb, news, bio)
        st.session_state.quiz_data = {"news": news, "bio": bio, "quiz": quiz}
        st.session_state.quiz_answers = {} # reset answers for new celeb

tabs = st.tabs(["ℹ️ Bio", "📰 Trending", "🎯 Quiz"])

# Tab 1: Bio inline
with tabs[0]:
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    if st.session_state.quiz_data:
        bio = st.session_state.quiz_data["bio"]
        c1, c2 = st.columns([1,3])
        with c1:
            if bio["img"]:
                st.image(bio["img"], use_container_width=True)
        with c2:
            st.header(bio["name"])
            st.write(f"**Category:** {bio['bio']}")
            st.write(bio["summary"]) # <-- now shows directly, no link-only
            st.markdown(f"[Read more on Wikipedia]({bio['url']})")
    else:
        st.info("Search a celebrity above to see bio here.")
    st.markdown('</div>', unsafe_allow_html=True)

# Tab 2: Trending News
with tabs[1]:
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    if st.session_state.quiz_data:
        news = st.session_state.quiz_data["news"]
        celeb = st.session_state.last_celeb
        st.subheader(f"Trending Now: {celeb}")
        if not news:
            st.info("No news found. Add NEWSAPI_KEY in.streamlit/secrets.toml for live data.")
        for n in news:
            st.markdown(f"**[{n['title']}]({n['url']})** \n*Source: {n['source']}*")
            st.divider()
    else:
        st.info("Search a celebrity above to see news here.")
    st.markdown('</div>', unsafe_allow_html=True)

# Tab 3: Quiz - fixed to not reset
with tabs[2]:
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    if st.session_state.quiz_data:
        quiz = st.session_state.quiz_data["quiz"]
        st.subheader("Celeb Quiz")
        # use form so clicking doesn't rerun until submit
        with st.form("quiz_form"):
            for i,q in enumerate(quiz):
                st.session_state.quiz_answers[i] = st.radio(
                    q["q"], q["opts"], key=f"q{i}"
                )
            submitted = st.form_submit_button("Check All Answers")
        if submitted:
            score = sum(1 for i,q in enumerate(quiz) if st.session_state.quiz_answers[i] == q["a"])
            st.success(f"Your Score: {score}/{len(quiz)} 🎉")
            for i,q in enumerate(quiz):
                if st.session_state.quiz_answers[i]!= q["a"]:
                    st.error(f"Q{i+1}: Correct answer → {q['a']}")
    else:
        st.info("Search a celebrity above to generate a quiz.")
    st.markdown('</div>', unsafe_allow_html=True)