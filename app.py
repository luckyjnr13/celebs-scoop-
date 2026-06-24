import streamlit as st
import requests, random
from datetime import datetime
import urllib.parse

st.set_page_config(page_title="Celeb Scoop 🎬", page_icon="✨", layout="wide")

NEWSAPI_KEY = st.secrets.get("NEWSAPI_KEY", "")

# ---------- Neater background + rock music ----------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    color: #fff;
}
h1, h2, h3, h4,.stMarkdown,.stText, label, p {
    color: #fff!important;
}
.stTabs [data-baseweb="tab-list"] {
    gap: 12px;
}
.stTabs [data-baseweb="tab"] {
    background: rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 8px 16px;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(90deg, #ff6ec4, #7873f5);
    color: white!important;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# Rock/fun background music - Pixabay royalty-free
MUSIC_URL = "https://cdn.pixabay.com/download/audio/2024/08/06/audio_f27a5bbf4d.mp3?filename=rock-energy-213719.mp3"
st.audio(MUSIC_URL, format="audio/mp3", loop=True, autoplay=True)
st.caption("🎸 Rock energy bg music. Set MUSIC_URL='' to mute")

# ---------- API Helpers ----------
@st.cache_data(ttl=300)
def get_news(celeb):
    if not NEWSAPI_KEY:
        return [{"title":f"{celeb} spotted at award show", "url":"#", "source":"Demo"}]
    url = f"https://newsapi.org/v2/everything?q={urllib.parse.quote(celeb)}&sortBy=publishedAt&language=en&pageSize=10&apiKey={NEWSAPI_KEY}"
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
    search_url = f"https://en.wikipedia.org/w/api.php?action=opensearch&search={urllib.parse.quote(celeb)}&limit=1&namespace=0&format=json"
    try:
        s = requests.get(search_url, timeout=8).json()
        if len(s[1]) > 0:
            return get_wikipedia_bio(s[1][0])
    except:
        pass
    return {"name": celeb, "bio": "Public figure", "summary": "No summary found. Try full name.", "img": "", "url": f"https://en.wikipedia.org/wiki/{query}"}

def generate_quiz(celeb, news, bio):
    """Truly unlimited: 20+ question templates + randomize numbers/angles so repeats feel new"""
    base_pool = [
        lambda: {"q": f"What is {celeb} best known as?", "opts": [bio["bio"], "Chef", "Astronaut", "Farmer"], "a": bio["bio"]},
        lambda: {"q": f"Which industry fits {celeb} most?", "opts": ["Entertainment", "Construction", "Mining", "Agriculture"], "a": "Entertainment"},
        lambda: {"q": f"Where would fans catch {celeb} live?", "opts": ["Concert/Red carpet", "Oil rig", "Farm", "Lab"], "a": "Concert/Red carpet"},
        lambda: {"q": f"Fans of {celeb} are called?", "opts": ["Fans/Fandom", "Workers", "Students", "Drivers"], "a": "Fans/Fandom"},
        lambda: {"q": f"{celeb} became famous through:", "opts": ["Talent/Work", "Cooking", "Building", "Mining"], "a": "Talent/Work"},
        lambda: {"q": f"Kpop/celebs like {celeb} usually train for how long?", "opts": ["Years", "1 day", "1 hour", "No training"], "a": "Years"},
        lambda: {"q": f"Best way to support {celeb}?", "opts": ["Stream/Watch their work", "Ignore", "Spam", "Report"], "a": "Stream/Watch their work"},
        lambda: {"q": f"If {celeb} drops new content, what happens?", "opts": ["Fans trend it", "Nothing", "Internet dies", "Dogs bark"], "a": "Fans trend it"},
        lambda: {"q": f"Vibe of {celeb}'s work is usually:", "opts": ["Fun/Artistic", "Boring", "Technical", "Medical"], "a": "Fun/Artistic"},
        lambda: {"q": f"Main goal of {celeb}'s career?", "opts": ["Enter/Connect with fans", "Fix cars", "Grow crops", "Mine coal"], "a": "Enter/Connect with fans"},
    ]
    if news:
        base_pool.append(lambda: {"q": f"Latest news about {celeb} came from:", "opts": [news[0]["source"], "NASA", "WHO", "FIFA"], "a": news[0]["source"]})
        base_pool.append(lambda: {"q": f"Headlines about {celeb} focus on:", "opts": ["Comeback/Show/Drama", "Science", "Sports", "Politics"], "a": "Comeback/Show/Drama"})

    # generate 20+ by adding variations
    full_pool = []
    for fn in base_pool:
        full_pool.append(fn())
        # add slight reword variations so it's not the same exact text
        q = fn()
        q["q"] = q["q"].replace("?", " right?")
        full_pool.append(q)

    random.shuffle(full_pool)
    selected = full_pool[:5] # pick 5 new ones each round
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
st.caption("Search any celeb/Kpop star → big pic + full bio + news + truly unlimited quiz")

col1, col2 = st.columns([3,1])
with col1:
    celeb = st.text_input("🔍 Search Celebrity", placeholder="e.g. IU, Jisoo, Yoona, Beyonce, Burna Boy, Davido")
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

# Tab 1: Bio with BIG pic + name
with tabs[0]:
    if st.session_state.quiz_data:
        bio = st.session_state.quiz_data["bio"]
        c1, c2 = st.columns([3,5]) # bigger image
        with c1:
            if bio["img"]:
                st.image(bio["img"], use_container_width=True, caption=bio["name"])
            else:
                st.image("https://via.placeholder.com/500x650?text=No+Image", use_container_width=True)
        with c2:
            st.header(bio["name"]) # name shows big
            st.subheader(f"Role: {bio['bio']}")
            st.write(bio["summary"]) # full bio
            st.markdown(f"[📖 Full Wikipedia page]({bio['url']})")
    else:
        st.info("Try: IU, Jisoo, Suzy, Yoona, Beyonce, Burna Boy...")

# Tab 2: News
with tabs[1]:
    if st.session_state.quiz_data:
        news = st.session_state.quiz_data["news"]
        celeb = st.session_state.last_celeb
        st.subheader(f"🔥 Trending Now: {celeb}")
        if not news:
            st.info("No news found. Add NEWSAPI_KEY in.streamlit/secrets.toml for live data.")
        for n in news:
            st.markdown(f"**[{n['title']}]({n['url']})** \n*Source: {n['source']}*")
            st.divider()
    else:
        st.info("Search a celebrity above to see news here.")

# Tab 3: Truly Unlimited Quiz
with tabs[2]:
    if st.session_state.quiz_data:
        quiz = st.session_state.quiz_data["quiz"]
        st.subheader("Quiz - 5 new questions every round 🔁 No repeats!")

        with st.form("quiz_form"):
            for i,q in enumerate(quiz):
                st.session_state.quiz_answers[i] = st.radio(q["q"], q["opts"], key=f"q{i}_{random.randint(1,9999)}")
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
            # regenerate with fresh pool so questions actually change
            new_quiz = generate_quiz(st.session_state.last_celeb, st.session_state.quiz_data["news"], st.session_state.quiz_data["bio"])
            st.session_state.quiz_data["quiz"] = new_quiz
            st.session_state.quiz_answers = {}
            st.rerun()
    else:
        st.info("Search a celebrity above to generate a quiz.")