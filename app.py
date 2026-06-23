import streamlit as st
import requests, random, base64
from datetime import datetime
import urllib.parse

st.set_page_config(page_title="Celeb Scoop 🎬", page_icon="✨", layout="wide")

# ---------- Secrets ----------
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

# ---------- Music player ----------
def music_player():
    try:
        with open("assets/theme.mp3", "rb") as f:
            data = f.read()
        b64 = base64.b64encode(data).decode()
        st.audio(f"data:audio/mp3;base64,{b64}", format="audio/mp3", loop=True)
    except:
        st.caption("Add assets/theme.mp3 for background music")

# ---------- API Helpers ----------
@st.cache_data(ttl=300) # refresh every 5 min
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
    """No API key needed. Gets summary + image from Wikipedia"""
    query = urllib.parse.quote(celeb.replace(" ", "_"))
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{query}"
    try:
        r = requests.get(url, timeout=8).json()
        if r.get("type") == "disambiguation":
            # pick first option
            return None
        summary = r.get("extract", f"{celeb} is a trending celebrity.")
        img = r.get("thumbnail", {}).get("source", "")
        desc = r.get("description", "Celebrity/Public figure")
        return {"name": r.get("title", celeb), "bio": desc, "summary": summary, "img": img}
    except:
        return {"name": celeb, "bio": "Public figure", "summary": "No Wikipedia summary found.", "img": ""}

# ---------- Quiz Generator ----------
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

# ---------- UI ----------
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
    with st.spinner(f"Scooping {celeb}..."):
        news = get_news(celeb)
        bio = get_wikipedia_bio(celeb)
        quiz = generate_quiz(celeb, news, bio)

        tabs = st.tabs(["ℹ️ Bio", "📰 Trending", "🎯 Quiz"])

        # Tab 1: Bio from Wikipedia
        with tabs[0]:
            st.markdown('<div class="glass">', unsafe_allow_html=True)
            if bio:
                c1, c2 = st.columns([1,3])
                with c1:
                    if bio["img"]:
                        st.image(bio["img"], use_column_width=True)
                with c2:
                    st.header(bio["name"])
                    st.write(f"**Category:** {bio['bio']}")
                    st.write(bio["summary"])
                    st.markdown(f"[Read more on Wikipedia](https://en.wikipedia.org/wiki/{urllib.parse.quote(bio['name'])})")
            else:
                st.warning("No Wikipedia page found. Try full name or different spelling.")
            st.markdown('</div>', unsafe_allow_html=True)

        # Tab 2: Trending News
        with tabs[1]:
            st.markdown('<div class="glass">', unsafe_allow_html=True)
            st.subheader(f"Trending Now: {celeb}")
            if not news:
                st.info("No news found. Add NEWSAPI_KEY in.streamlit/secrets.toml for live data.")
            for n in news:
                st.markdown(f"**[{n['title']}]({n['url']})** \n*Source: {n['source']}*")
                st.divider()
            st.markdown('</div>', unsafe_allow_html=True)

        # Tab 3: Quiz
        with tabs[2]:
            st.markdown('<div class="glass">', unsafe_allow_html=True)
            st.subheader("Celeb Quiz - Refreshes with each search")
            score = 0
            for i,q in enumerate(quiz):
                ans = st.radio(q["q"], q["opts"], key=f"q{i}")
                if st.button(f"Check Q{i+1}", key=f"b{i}"):
                    if ans == q["a"]:
                        st.success("Correct! 🎉")
                        score += 1
                    else:
                        st.error(f"Answer: {q['a']}")
            st.metric("Your Score", f"{score}/{len(quiz)}")
            st.markdown('</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="glass"><h3>How it works</h3><p>1. Type any celeb name<br>2. Hit "Scoop It!"<br>3. Get Wikipedia bio + live news + quiz<br>4. Toggle music above</p></div>', unsafe_allow_html=True)
    st.info("Only NEWSAPI_KEY needed now. Get free key at newsapi.org")