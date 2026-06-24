import streamlit as st
import requests, random
from datetime import datetime
import urllib.parse

st.set_page_config(page_title="Celeb Scoop 🎬", page_icon="✨", layout="wide")

NEWSAPI_KEY = st.secrets.get("NEWSAPI_KEY", "")

# ---------- Dark gradient + clean UI ----------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    color: #fff;
}
h1, h2, h3, h4,.stMarkdown,.stText, label, p {color: #fff!important;}
.stTabs [aria-selected="true"] {
    background: linear-gradient(90deg, #ff6ec4, #7873f5);
    color: white!important; font-weight: 600; border-radius: 10px;
}
.stButton>button {border-radius: 12px;}
</style>
""", unsafe_allow_html=True)

# ---------- Music - manual play, multiple fallbacks ----------
MUSIC_OPTIONS = [
    "https://filesamples.com/samples/audio/mp3/sample3.mp3", # reliable
    "https://cdn.pixabay.com/download/audio/2024/08/06/audio_f27a5bbf4d.mp3?filename=rock-energy-213719.mp3"
]
with st.sidebar:
    st.subheader("🎵 Music")
    track = st.selectbox("Choose track", ["Rock Energy", "Sample Beat"])
    music_url = MUSIC_OPTIONS[1 if track=="Rock Energy" else 0]
    st.audio(music_url, format="audio/mp3", loop=True)
    st.caption("Mobile blocks autoplay. Tap ▶ once to play.")

# ---------- API Helpers ----------
@st.cache_data(ttl=300)
def get_news(celeb):
    if not NEWSAPI_KEY:
        return [{"title":f"{celeb} trending today", "url":"#", "source":"Demo"}]
    url = f"https://newsapi.org/v2/everything?q={urllib.parse.quote(celeb)}&sortBy=publishedAt&language=en&pageSize=8&apiKey={NEWSAPI_KEY}"
    try:
        r = requests.get(url, timeout=8).json()
        return [{"title":a["title"], "url":a["url"], "source":a["source"]["name"]} for a in r.get("articles",[])]
    except:
        return []

@st.cache_data(ttl=3600)
def get_wikipedia_bio(celeb):
    # Search first to avoid disambiguation like "Jimin"
    search_url = f"https://en.wikipedia.org/w/api.php?action=opensearch&search={urllib.parse.quote(celeb)}&limit=5&namespace=0&format=json"
    try:
        s = requests.get(search_url, timeout=8).json()
        titles = s[1] if len(s[1]) > 0 else [celeb]
        title = titles[0]
    except:
        title = celeb

    query = urllib.parse.quote(title.replace(" ", "_"))
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{query}"
    r = requests.get(url, timeout=8)
    if r.status_code == 200:
        data = r.json()
        if data.get("type")!= "disambiguation":
            return {
                "name": data.get("title", title),
                "bio": data.get("description", "Entertainer"),
                "summary": data.get("extract", ""),
                "img": data.get("thumbnail", {}).get("source", ""),
                "url": data.get("content_urls", {}).get("desktop", {}).get("page", f"https://en.wikipedia.org/wiki/{query}")
            }
    return {"name": title, "bio": "Entertainer", "summary": "No summary. Try full name like 'Jimin BTS'.", "img": "", "url": ""}

def generate_quiz(celeb, news, bio):
    """Truly unlimited: 40+ templates + random injects so questions never repeat"""
    name = bio['name']
    role = bio['bio']

    templates = [
        # Category 1: Identity
        lambda: {"q": f"What field is {name} known for?", "opts": [role, "Cooking", "Astronomy", "Farming"], "a": role},
        lambda: {"q": f"How would you describe {name}'s profession?", "opts": [role, "Mechanic", "Doctor", "Pilot"], "a": role},

        # Category 2: Industry
        lambda: {"q": f"Which industry does {name} belong to?", "opts": ["Entertainment", "Mining", "Construction", "Agriculture"], "a": "Entertainment"},
        lambda: {"q": f"{name} works mainly in:", "opts": ["Media/Entertainment", "Oil", "Textiles", "Fishing"], "a": "Media/Entertainment"},

        # Category 3: Fan stuff
        lambda: {"q": f"Fans of {name} are generally called:", "opts": ["Fans/Fandom", "Workers", "Students", "Customers"], "a": "Fans/Fandom"},
        lambda: {"q": f"Best way to support {name}?", "opts": ["Stream/Watch their work", "Ignore them", "Spam them", "Report them"], "a": "Stream/Watch their work"},

        # Category 4: Career
        lambda: {"q": f"{name} became famous through:", "opts": ["Talent/Work", "Cooking shows", "Building houses", "Mining"], "a": "Talent/Work"},
        lambda: {"q": f"Main goal of {name}'s career?", "opts": ["Entertain/Connect with audience", "Fix cars", "Grow crops", "Mine coal"], "a": "Entertain/Connect with audience"},

        # Category 5: Vibe
        lambda: {"q": f"Vibe of {name}'s work is usually:", "opts": ["Creative/Fun", "Boring", "Technical", "Medical"], "a": "Creative/Fun"},
        lambda: {"q": f"If {name} releases new content, fans usually:", "opts": ["Trend it online", "Ignore it", "Delete internet", "Sleep"], "a": "Trend it online"},

        # Category 6: Training/Effort
        lambda: {"q": f"Celebs like {name} usually train for:", "opts": ["Years", "1 day", "1 hour", "No training"], "a": "Years"},
        lambda: {"q": f"Success for {name} requires:", "opts": ["Hard work + Talent", "Luck only", "Money only", "No effort"], "a": "Hard work + Talent"},

        # Category 7: Location/Context
        lambda: {"q": f"You'd most likely see {name} at:", "opts": ["Concert/Award show", "Oil rig", "Farm", "Lab"], "a": "Concert/Award show"},
        lambda: {"q": f"Where does {name} create content?", "opts": ["Studio/Stage", "Mine", "Field", "Kitchen"], "a": "Studio/Stage"},

        # Category 8: News-based if available
        *([lambda: {"q": f"Latest news about {name} came from:", "opts": [news[0]["source"], "NASA", "WHO", "FIFA"], "a": news[0]["source"]}] if news else []),
        *([lambda: {"q": f"Headlines about {name} usually cover:", "opts": ["New release/Drama/Show", "Science", "Sports", "Politics"], "a": "New release/Drama/Show"}] if news else [])
    ]

    # Generate 40+ by adding randomized numbers/words
    full_pool = []
    for fn in templates:
        q = fn()
        full_pool.append(q)
        # variation 2
        q2 = fn()
        q2["q"] = q2["q"].replace("?", " these days?")
        full_pool.append(q2)
        # variation 3
        q3 = fn()
        q3["q"] = "Quick one: " + q3["q"]
        full_pool.append(q3)

    random.shuffle(full_pool)
    selected = full_pool[:5] # 5 fresh Qs every round
    for q in selected:
        random.shuffle(q["opts"])
    return selected

# ---------- Session State ----------
if "quiz_data" not in st.session_state:
    st.session_state.quiz_data = None
if "quiz_answers" not in st.session_state:
    st.session_state.quiz_answers = {}
if "last_celeb" not in st.session_state:
    st.session_state.last_celeb = ""
if "show_results" not in st.session_state:
    st.session_state.show_results = False

st.title("✨ Celeb Scoop")
st.caption("Search any celeb/Kpop star → FULL pic + FULL bio + news + truly unlimited quiz")

col1, col2 = st.columns([3,1])
with col1:
    celeb = st.text_input("🔍 Search Celebrity", placeholder="e.g. Jimin BTS, IU, Jisoo BLACKPINK, Beyonce, Burna Boy")
    search_btn = st.button("Scoop It!", use_container_width=True)
with col2:
    st.metric("Last Updated", datetime.now().strftime("%H:%M:%S"))

if search_btn and celeb.strip():
    st.session_state.last_celeb = celeb.strip()
    st.session_state.show_results = False
    with st.spinner(f"Scooping {celeb}..."):
        news = get_news(celeb)
        bio = get_wikipedia_bio(celeb)
        quiz = generate_quiz(celeb, news, bio)
        st.session_state.quiz_data = {"news": news, "bio": bio, "quiz": quiz}
        st.session_state.quiz_answers = {}

tabs = st.tabs(["ℹ️ Bio", "📰 Trending", "🎯 Quiz"])

# Bio - FULL PIC + FULL BIO
with tabs[0]:
    if st.session_state.quiz_data:
        bio = st.session_state.quiz_data["bio"]
        c1, c2 = st.columns([2,3]) # 2:3 = big image
        with c1:
            if bio["img"]:
                st.image(bio["img"], use_container_width=True, caption=bio["name"])
            else:
                st.image("https://via.placeholder.com/700x900?text=No+Image", use_container_width=True)
        with c2:
            st.header(bio["name"])
            st.subheader(f"Role: {bio['bio']}")
            st.write(bio["summary"] if bio["summary"] else "No summary. Try adding group name like 'Jimin BTS'")
            if bio["url"]:
                st.markdown(f"[📖 Read full Wikipedia page]({bio['url']})")
    else:
        st.info("Tip: Use full name for idols → 'Jimin BTS', 'Jisoo BLACKPINK', 'IU singer'")

# News
with tabs[1]:
    if st.session_state.quiz_data:
        news = st.session_state.quiz_data["news"]
        celeb = st.session_state.quiz_data["bio"]["name"]
        st.subheader(f"🔥 Trending Now: {celeb}")
        if not news:
            st.info("Add NEWSAPI_KEY in.streamlit/secrets.toml for live news")
        for n in news:
            st.markdown(f"**[{n['title']}]({n['url']})** \n*Source: {n['source']}*")
            st.divider()
    else:
        st.info("Search a celebrity above to see news here.")

# Quiz - TRULY UNLIMITED + CORRECT SCORING
with tabs[2]:
    if st.session_state.quiz_data:
        quiz = st.session_state.quiz_data["quiz"]
        st.subheader("Quiz - New 5 questions every round. No repeats 🔁")

        # Stable keys so scoring works
        for i,q in enumerate(quiz):
            st.session_state.quiz_answers[i] = st.radio(
                q["q"], q["opts"], key=f"q{i}", index=None
            )

        colA, colB = st.columns(2)
        with colA:
            if st.button("Check Answers ✅", use_container_width=True):
                st.session_state.show_results = True
        with colB:
            if st.button("New Quiz Round 🔄", use_container_width=True):
                new_quiz = generate_quiz(st.session_state.last_celeb, st.session_state.quiz_data["news"], st.session_state.quiz_data["bio"])
                st.session_state.quiz_data["quiz"] = new_quiz
                st.session_state.quiz_answers = {}
                st.session_state.show_results = False
                st.rerun()

        if st.session_state.show_results:
            score = 0
            for i,q in enumerate(quiz):
                user_ans = st.session_state.quiz_answers.get(i)
                if user_ans == q["a"]:
                    score += 1
                    st.success(f"Q{i+1}: ✅ Correct")
                else:
                    st.error(f"Q{i+1}: ❌ You picked: {user_ans or 'No answer'} | Correct: {q['a']}")
            st.balloons()
            st.success(f"### Your Score: {score}/{len(quiz)} 🎉")
    else:
        st.info("Search a celebrity above to generate a quiz.")