import streamlit as st
import requests, random
from datetime import datetime

st.set_page_config(page_title="Celeb Scoop 🎬", page_icon="✨", layout="wide")

NEWSAPI_KEY = st.secrets.get("NEWSAPI_KEY", "")

st.markdown("""
<style>
.stApp {background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%); color: #fff;}
h1,h2,h3,h4,.stMarkdown,.stText,label,p {color: #fff!important;}
.stTabs [aria-selected="true"] {background: linear-gradient(90deg, #ff6ec4, #7873f5); color: white!important; font-weight: 600; border-radius: 10px;}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    if st.checkbox("🎵 Music", value=False):
        st.audio("https://filesamples.com/samples/audio/mp3/sample3.mp3", format="audio/mp3", loop=True)

@st.cache_data(ttl=300)
def get_news(celeb):
    if not NEWSAPI_KEY:
        return [{"title":f"{celeb} trending today", "url":"#", "source":"Demo"}]
    url = f"https://newsapi.org/v2/everything?q={celeb}&sortBy=publishedAt&language=en&pageSize=8&apiKey={NEWSAPI_KEY}"
    try:
        r = requests.get(url, timeout=8).json()
        return [{"title":a["title"], "url":a["url"], "source":a["source"]["name"]} for a in r.get("articles",[])]
    except:
        return []

@st.cache_data(ttl=3600)
def get_wikipedia_bio(celeb):
    """
    Bulletproof version:
    1. Search for page -> get pageid
    2. Use pageid to fetch extract + image.
    This works for 'Cardi B', 'Jimin BTS', 'Burna Boy' etc.
    """
    # Step 1: search
    search_url = "https://en.wikipedia.org/w/api.php"
    params = {"action":"query","list":"search","srsearch":celeb,"srlimit":3,"format":"json"}
    try:
        r = requests.get(search_url, params=params, timeout=8).json()
        results = r.get("query",{}).get("search",[])
        if not results:
            return {"name": celeb, "bio": "Public figure", "summary": "No Wikipedia page found.", "img": "", "url": ""}
        pageid = results[0]["pageid"]
        title = results[0]["title"]
    except:
        return {"name": celeb, "bio": "Public figure", "summary": "Wikipedia error.", "img": "", "url": ""}

    # Step 2: fetch content by pageid
    params = {
        "action":"query",
        "pageids": pageid,
        "prop":"extracts|pageimages",
        "exintro": True,
        "explaintext": True,
        "pithumbsize": 1000,
        "format":"json"
    }
    try:
        r = requests.get(search_url, params=params, timeout=8).json()
        page = r["query"]["pages"][str(pageid)]
        extract = page.get("extract","")
        img = page.get("thumbnail",{}).get("source","")
        first_line = extract.split("\n")[0] if extract else "Entertainer"
        return {
            "name": title,
            "bio": first_line[:100] + "..." if len(first_line)>100 else first_line,
            "summary": extract,
            "img": img,
            "url": f"https://en.wikipedia.org/?curid={pageid}"
        }
    except:
        return {"name": title, "bio": "Public figure", "summary": "Could not load details.", "img": "", "url": ""}

def generate_quiz(celeb, news, bio):
    name = bio['name']
    role = bio['bio'].split(",")[0].split(".")[0]
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
    pool = [fn() for fn in templates for _ in range(3)]
    random.shuffle(pool)
    selected = pool[:5]
    for q in selected: random.shuffle(q["opts"])
    return selected

if "quiz_data" not in st.session_state: st.session_state.quiz_data = None
if "quiz_answers" not in st.session_state: st.session_state.quiz_answers = {}
if "last_celeb" not in st.session_state: st.session_state.last_celeb = ""
if "show_results" not in st.session_state: st.session_state.show_results = False

st.title("✨ Celeb Scoop")
col1, col2 = st.columns([3,1])
with col1:
    celeb = st.text_input("🔍 Search Celebrity", placeholder="Cardi B, Jimin BTS, Burna Boy, IU, Beyonce")
    if st.button("Scoop It!", use_container_width=True) and celeb.strip():
        st.session_state.last_celeb = celeb.strip()
        st.session_state.show_results = False
        with st.spinner(f"Scooping {celeb}..."):
            news = get_news(celeb)
            bio = get_wikipedia_bio(celeb)
            quiz = generate_quiz(celeb, news, bio)
            st.session_state.quiz_data = {"news": news, "bio": bio, "quiz": quiz}
            st.session_state.quiz_answers = {}
with col2:
    st.metric("Last Updated", datetime.now().strftime("%H:%M:%S"))

tabs = st.tabs(["ℹ️ Bio", "📰 Trending", "🎯 Quiz"])

with tabs[0]:
    if st.session_state.quiz_data:
        bio = st.session_state.quiz_data["bio"]
        c1, c2 = st.columns([2,3])
        with c1:
            if bio["img"]: st.image(bio["img"], use_container_width=True, caption=bio["name"])
            else: st.image("https://via.placeholder.com/1000x1200?text=No+Image", use_container_width=True)
        with c2:
            st.header(bio["name"])
            st.subheader(f"Role: {bio['bio']}")
            st.write(bio["summary"] if bio["summary"] else "No summary.")
            if bio["url"]: st.markdown(f"[📖 Full Wikipedia]({bio['url']})")
    else:
        st.info("Try: Cardi B, Jimin BTS, Burna Boy...")

with tabs[1]:
    if st.session_state.quiz_data:
        news = st.session_state.quiz_data["news"]
        celeb = st.session_state.quiz_data["bio"]["name"]
        st.subheader(f"🔥 Trending: {celeb}")
        for n in news:
            st.markdown(f"**[{n['title']}]({n['url']})** \n*Source: {n['source']}*")
            st.divider()
    else: st.info("Search a celebrity above")

with tabs[2]:
    if st.session_state.quiz_data:
        quiz = st.session_state.quiz_data["quiz"]
        st.subheader("Quiz - 5 new questions every round")
        for i,q in enumerate(quiz):
            st.session_state.quiz_answers[i] = st.radio(q["q"], q["opts"], key=f"q{i}", index=None)
        colA, colB = st.columns(2)
        with colA:
            if st.button("Check Answers ✅", use_container_width=True): st.session_state.show_results = True
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
                if user_ans == q["a"]: st.success(f"Q{i+1}: ✅ Correct")
                else: st.error(f"Q{i+1}: ❌ You: {user_ans or 'No answer'} | Correct: {q['a']}")
            st.balloons()
            st.success(f"### Score: {score}/{len(quiz)} 🎉")
    else: st.info("Search a celebrity above")