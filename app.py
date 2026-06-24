import streamlit as st
import requests, random
from datetime import datetime
import urllib.parse

st.set_page_config(page_title="Celeb Scoop 🎬", page_icon="✨", layout="wide")

NEWSAPI_KEY = st.secrets.get("NEWSAPI_KEY", "")

# ---------- UI ----------
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
</style>
""", unsafe_allow_html=True)

# Music in sidebar - manual play
MUSIC_URL = "https://filesamples.com/samples/audio/mp3/sample3.mp3"
with st.sidebar:
    if st.checkbox("🎵 Play music", value=False):
        st.audio(MUSIC_URL, format="audio/mp3", loop=True)
        st.caption("Tap ▶ once. Mobile blocks autoplay")

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
    """
    FIX: Use action=query instead of rest_v1. Works for 'Cardi B', 'Burna Boy', etc.
    Tries multiple search results until we get a real page.
    """
    search_url = f"https://en.wikipedia.org/w/api.php?action=opensearch&search={urllib.parse.quote(celeb)}&limit=5&namespace=0&format=json"
    try:
        s = requests.get(search_url, timeout=8).json()
        titles = s[1] if len(s[1]) > 0 else [celeb]
    except:
        titles = [celeb]

    for title in titles:
        query = urllib.parse.quote(title.replace(" ", "_"))
        # More reliable API for full extract + image
        url = f"https://en.wikipedia.org/w/api.php?action=query&titles={query}&prop=extracts|pageimages&pithumbsize=800&exintro=true&explaintext=true&format=json"
        r = requests.get(url, timeout=8)
        if r.status_code == 200:
            data = r.json()
            pages = data.get("query", {}).get("pages", {})
            for pageid, page in pages.items():
                if pageid!= "-1": # page exists
                    extract = page.get("extract", "")
                    img = page.get("thumbnail", {}).get("source", "")
                    # First line = "description"
                    desc = extract.split("\n")[0][:80] + "..." if extract else "Entertainer"
                    return {
                        "name": page.get("title", title),
                        "bio": desc,
                        "summary": extract,
                        "img": img,
                        "url": f"https://en.wikipedia.org/wiki/{query}"
                    }
    # Last resort
    return {"name": celeb, "bio": "Public figure", "summary": "No Wikipedia page found. Check spelling.", "img": "", "url": ""}

def generate_quiz(celeb, news, bio):
    name = bio['name']
    role = bio['bio'].split(",")[0] # clean role

    templates = [
        lambda: {"q": f"What is {name} known for?", "opts": [role, "Cooking", "Astronomy", "Farming"], "a": role},
        lambda: {"q": f"Which industry fits {name}?", "opts": ["Entertainment", "Mining", "Construction", "Agriculture"], "a": "Entertainment"},
        lambda: {"q": f"Fans of {name} are called?", "opts": ["Fans/Fandom", "Workers", "Students", "Drivers"], "a": "Fans/Fandom"},
        lambda: {"q": f"{name} became famous through:", "opts": ["Talent/Work", "Cooking", "Building", "Mining"], "a": "Talent/Work"},
        lambda: {"q": f"Vibe of {name}'s work?", "opts": ["Creative/Fun", "Boring", "Technical", "Medical"], "a": "Creative/Fun"},
        lambda: {"q": f"Celebs like {name} train for:", "opts": ["Years", "1 day", "1 hour", "No training"], "a": "Years"},
        lambda: {"q": f"Best way to support {name}?", "opts": ["Stream/Watch their work", "Ignore", "Spam", "Report"], "a": "Stream/Watch their work"},
        lambda: {"q": f"You'd see {name} at:", "opts": ["Concert/Award show", "Oil rig", "Farm", "Lab"], "a": "Concert/Award show"},
    ]
    if news:
        templates.append(lambda: {"q": f"Latest news about {name} from:", "opts": [news[0]["source"], "NASA", "WHO", "FIFA"], "a": news[0]["source"]})

    pool = [fn() for fn in templates for _ in range(3)] # 3x variations
    random.shuffle(pool)
    selected = pool[:5]
    for q in selected:
        random.shuffle(q["opts"])
    return selected

# ---------- State ----------
if "quiz_data" not in st.session_state:
    st.session_state.quiz_data = None
if "quiz_answers" not in st.session_state:
    st.session_state.quiz_answers = {}
if "last_celeb" not in st.session_state:
    st.session_state.last_celeb = ""
if "show_results" not in st.session_state:
    st.session_state.show_results = False

st.title("✨ Celeb Scoop")
st.caption("Search any celeb → BIG pic + FULL bio + news + unlimited quiz")

col1, col2 = st.columns([3,1])
with col1:
    celeb = st.text_input("🔍 Search Celebrity", placeholder="Cardi B, Jimin BTS, IU, Burna Boy, Beyonce")
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

# Bio - BIG PIC + FULL TEXT
with tabs[0]:
    if st.session_state.quiz_data:
        bio = st.session_state.quiz_data["bio"]
        c1, c2 = st.columns([2,3])
        with c1:
            if bio["img"]:
                st.image(bio["img"], use_container_width=True, caption=bio["name"])
            else:
                st.image("https://via.placeholder.com/800x1000?text=No+Image+Found", use_container_width=True)
        with c2:
            st.header(bio["name"])
            st.subheader(f"Role: {bio['bio']}")
            st.write(bio["summary"] if bio["summary"] else "No summary found.")
            if bio["url"]:
                st.markdown(f"[📖 Full Wikipedia page]({bio['url']})")
    else:
        st.info("Try: Cardi B, Jimin BTS, IU, Burna Boy...")

# News
with tabs[1]:
    if st.session_state.quiz_data:
        news = st.session_state.quiz_data["news"]
        celeb = st.session_state.quiz_data["bio"]["name"]
        st.subheader(f"🔥 Trending: {celeb}")
        for n in news:
            st.markdown(f"**[{n['title']}]({n['url']})** \n*Source: {n['source']}*")
            st.divider()
    else:
        st.info("Search a celebrity above")

# Quiz
with tabs[2]:
    if st.session_state.quiz_data:
        quiz = st.session_state.quiz_data["quiz"]
        st.subheader("Quiz - 5 new questions every round")

        for i,q in enumerate(quiz):
            st.session_state.quiz_answers[i] = st.radio(q["q"], q["opts"], key=f"q{i}", index=None)

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
            score = sum(1 for i,q in enumerate(quiz) if st.session_state.quiz_answers.get(i) == q["a"])
            for i,q in enumerate(quiz):
                user_ans = st.session_state.quiz_answers.get(i)
                if user_ans == q["a"]:
                    st.success(f"Q{i+1}: ✅ Correct")
                else:
                    st.error(f"Q{i+1}: ❌ You: {user_ans or 'No answer'} | Correct: {q['a']}")
            st.balloons()
            st.success(f"### Score: {score}/{len(quiz)} 🎉")
    else:
        st.info("Search a celebrity above")