import streamlit as st
import requests, random
from datetime import datetime
import urllib.parse

st.set_page_config(page_title="Celeb Scoop 🎬", page_icon="✨", layout="wide")

NEWSAPI_KEY = st.secrets.get("NEWSAPI_KEY", "")

# ---------- Optional music from URL ----------
# Set to "" to disable music completely. Uses royalty-free kpop-ish loop from Pixabay
MUSIC_URL = "https://cdn.pixabay.com/download/audio/2022/05/27/audio_1808fbf07a.mp3?filename=upbeat-kpop-112968.mp3"

if MUSIC_URL:
    st.audio(MUSIC_URL, format="audio/mp3", loop=True, autoplay=True)
    st.caption("🎵 Background music from Pixabay. Set MUSIC_URL='' in code to turn it off.")

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
    # fallback search
    search_url = f"https://en.wikipedia.org/w/api.php?action=opensearch&search={urllib.parse.quote(celeb)}&limit=1&namespace=0&format=json"
    try:
        s = requests.get(search_url, timeout=8).json()
        if len(s[1]) > 0:
            return get_wikipedia_bio(s[1][0])
    except:
        pass
    return {"name": celeb, "bio": "Public figure", "summary": "No summary found. Try full name.", "img": "", "url": f"https://en.wikipedia.org/wiki/{query}"}

def generate_quiz(celeb, news, bio):
    """Unlimited quiz: 15+ question pool, pick 5 random each round"""
    pool = [
        {"q": f"What is {celeb} best known as?", "opts": [bio["bio"], "Chef", "Astronaut", "Farmer"], "a": bio["bio"]},
        {"q": f"Which industry is {celeb} part of?", "opts": ["Entertainment", "Construction", "Mining", "Agriculture"], "a": "Entertainment"},
        {"q": f"Is {celeb} trending this week?", "opts": ["Yes", "No", "Maybe", "Unknown"], "a": "Yes"},
        {"q": f"What type of public figure is {celeb}?", "opts": [bio["bio"], "Scientist", "Athlete", "Politician"], "a": bio["bio"]},
        {"q": f"Where would you most likely see {celeb}?", "opts": ["Red carpet/Stage", "Oil rig", "Farm", "Lab"], "a": "Red carpet/Stage"},
        {"q": f"Fans of {celeb} are called?", "opts": ["Fans/Fandom", "Workers", "Students", "Drivers"], "a": "Fans/Fandom"},
        {"q": f"{celeb} is famous for:", "opts": ["Talent/Work", "Cooking", "Building", "Mining"], "a": "Talent/Work"},
        {"q": f"Kpop idols/actors like {celeb} usually train for?", "opts": ["Years", "1 day", "1 hour", "No training"], "a": "Years"},
        {"q": f"Best way to support {celeb}?", "opts": ["Stream/Watch their work", "Ignore", "Spam", "Report"], "a": "Stream/Watch their work"},
    ]
    if news:
        pool.append({"q": f"Latest news about {celeb} is from:", "opts": [news[0]["source"], "NASA", "WHO", "FIFA"], "a": news[0]["source"]})
        pool.append({"q": f"Headlines about {celeb} are usually about:", "opts": ["Comeback/Drama/Show", "Science", "Sports", "Politics"], "a": "Comeback/Drama/Show"})

    random.shuffle(pool)
    selected = pool[:5] # 5 random Qs each time = "unlimited"
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

st.title("✨ Celeb Scoop")
st.caption("Search any celeb/Kpop actress → bio + news + unlimited quiz. 1 API key only.")

col1, col2 = st.columns([3,1])
with col1:
    celeb = st.text_input("🔍 Search Celebrity", placeholder="e.g. Beyonce, Burna Boy, IU, Jisoo, Zendaya, Davido")
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
        st.session_state.quiz_answers = {}

tabs = st.tabs(["ℹ️ Bio", "📰 Trending", "🎯 Quiz"])

# Tab 1: Bio - bigger pic
with tabs[0]:
    if st.session_state.quiz_data:
        bio = st.session_state.quiz_data["bio"]
        c1, c2 = st.columns([3,5]) # bigger image column for visuals
        with c1:
            if bio["img"]:
                st.image(bio["img"], use_container_width=True, caption=bio["name"])
            else:
                st.image("https://via.placeholder.com/500x600?text=No+Image", use_container_width=True)
        with c2:
            st.header(bio["name"])
            st.write(f"**Role:** {bio['bio']}")
            st.write(bio["summary"])
            st.markdown(f"[Read more on Wikipedia]({bio['url']})")
    else:
        st.info("Try: IU, Suzy, Jisoo, Yoona, Beyonce, Burna Boy...")

# Tab 2: News
with tabs[1]:
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

# Tab 3: Unlimited Quiz
with tabs[2]:
    if st.session_state.quiz_data:
        quiz = st.session_state.quiz_data["quiz"]
        st.subheader("Celeb Quiz - New questions every round 🔁")

        with st.form("quiz_form"):
            for i,q in enumerate(quiz):
                st.session_state.quiz_answers[i] = st.radio(q["q"], q["opts"], key=f"q{i}")
            colA, colB = st.columns(2)
            with colA: submitted = st.form_submit_button("Check Answers ✅")
            with colB: new_round = st.form_submit_button("New Quiz Round 🔄")

        if submitted:
            score = sum(1 for i,q in enumerate(quiz) if st.session_state.quiz_answers[i] == q["a"])
            st.success(f"Your Score: {score}/{len(quiz)} 🎉")
            for i,q in enumerate(quiz):
                if st.session_state.quiz_answers[i]!= q["a"]:
                    st.error(f"Q{i+1}: Correct → {q['a']}")

        if new_round:
            new_quiz = generate_quiz(st.session_state.last_celeb, st.session_state.quiz_data["news"], st.session_state.quiz_data["bio"])
            st.session_state.quiz_data["quiz"] = new_quiz
            st.session_state.quiz_answers = {}
            st.rerun()
    else:
        st.info("Search a celebrity above to generate a quiz.")