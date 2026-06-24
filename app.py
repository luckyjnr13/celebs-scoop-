import streamlit as st
import requests, random
import urllib.parse

st.set_page_config(page_title="Celeb Scoop ∞ Jennie Mode", page_icon="🎤", layout="wide")

# ---------- Jennie / BLACKPINK Kpop UI ----------
st.markdown("""
<style>
.stApp {background: linear-gradient(135deg, #ff758c 0%, #ff7eb3 30%, #9f7aea 100%); color: #1a1a1a;}
h1,h2,h3,h4,.stMarkdown,.stText,label,p {color: #1a1a1a!important; font-family: 'Segoe UI', sans-serif;}
.stTabs [aria-selected="true"] {background: linear-gradient(90deg, #f093fb, #f5576c); color: white!important; font-weight: 700; border-radius: 14px;}
.stButton>button {background: linear-gradient(90deg, #f093fb, #f5576c); color: white; border: none; border-radius: 14px; font-weight: 700; padding: 0.6rem 1rem;}
div[data-testid="stMetricValue"] {font-size: 32px; color: #ff2e88!important;}
</style>
""", unsafe_allow_html=True)

# ---------- Sidebar + Background Music ----------
with st.sidebar:
    st.header("💗 Jennie Mode")
    st.caption("Pink + purple vibes + Kpop beats")

    music_on = st.toggle("🔊 Kpop Background", value=True)
    if music_on:
        # Single track only. Streamlit can't loop a playlist. User can hit loop icon on player
        st.audio(
            "https://cdn.pixabay.com/download/audio/2023/05/09/audio_c8c8a73467.mp3?filename=kpop-179923.mp3",
            format="audio/mp3"
        )
        st.caption("Tap ▶ once. Mobile blocks autoplay. Hit loop icon on player for endless play")

HEADERS = {"User-Agent": "CelebScoopJennie/2.2"}

# ---------- Data: Wikipedia + Last.fm ----------
@st.cache_data(ttl=3600)
def get_wikipedia(name):
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(name.replace(' ', '_'))}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10).json()
        if r.get("type") == "disambiguation" or r.get("title") == "Not found.":
            return None
        bio = r.get("extract", "")
        img = r.get("original", {}).get("source") or r.get("thumbnail", {}).get("source", "")
        return {
            "name": r.get("title", name),
            "bio": bio,
            "images": [img] if img else [],
            "url": r.get("content_urls",{}).get("desktop",{}).get("page","")
        }
    except:
        return None

@st.cache_data(ttl=3600)
def get_lastfm(name):
    url = f"http://ws.audioscrobbler.com/2.0/?method=artist.getinfo&artist={urllib.parse.quote(name)}&format=json"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10).json()
        if "error" in r:
            return None
        a = r.get("artist", {})
        bio = a.get("bio", {}).get("summary", "").split("<a href")[0].strip()
        imgs = [img["#text"] for img in a.get("image", []) if img["#text"] and img["size"] in ["extralarge", "mega"]]
        return {
            "name": a.get("name", name),
            "bio": bio,
            "images": imgs[:6],
            "url": a.get("url", "")
        }
    except:
        return None

def get_celeb_data(name):
    wiki = get_wikipedia(name)
    lastfm = get_lastfm(name)
    if wiki and len(wiki.get("bio","")) > 50:
        imgs = wiki["images"][:]
        if lastfm:
            imgs += [u for u in lastfm["images"] if u not in imgs]
        wiki["images"] = imgs[:8]
        return wiki
    if lastfm:
        return lastfm
    return {"name": name, "bio": "No data found. Try full name like 'Jennie BLACKPINK'", "images": [], "url": ""}

# ---------- Unlimited question generator ----------
def question_pool(celeb):
    name = celeb["name"]
    genres = ["K-pop", "Pop", "Hip-hop", "R&B", "Dance", "Ballad"]
    countries = ["Korea", "USA", "Japan", "UK", "Nigeria"]
    return [
        {"q": f"Is {name} a public figure/celebrity?", "opts": ["Yes","No","Maybe","Bot"], "a": "Yes"},
        {"q": f"Best way to support {name}?", "opts": ["Stream/Watch","Ignore","Spam","Report"], "a": "Stream/Watch"},
        {"q": f"Would {name} perform on stage?", "opts": ["Yes","No","Only in dreams","Never"], "a": "Yes"},
        {"q": f"Primary genre of {name}?", "opts": [random.choice(genres),"Cooking","Car repair","Farming"], "a": random.choice(genres)},
        {"q": f"Does {name} have fans/fandom?", "opts": ["Yes","No","3 people","Zero"], "a": "Yes"},
        {"q": f"Where would you see {name} live?", "opts": ["Concert/MV","Oil rig","Farm","Space"], "a": "Concert/MV"},
        {"q": f"Is {name} active internationally?", "opts": ["Yes","No","Only locally","Mars"], "a": "Yes"},
        {"q": f"Main platform for {name}?", "opts": ["Spotify/YouTube/IG/TikTok","Fax","Telegram","Morse"], "a": "Spotify/YouTube/IG/TikTok"},
        {"q": f"Would {name} release music/content?", "opts": ["Yes","No","Used to","Retired"], "a": "Yes"},
        {"q": f"Is {name} connected to {random.choice(countries)}?", "opts": ["Could be","No","Atlantis","Moon"], "a": "Could be"},
        {"q": f"Do fans make edits of {name}?", "opts": ["Yes","No","Never","What are edits"], "a": "Yes"},
        {"q": f"Is {name} trending online?", "opts": ["Often","Never","Only offline","On radio 1950"], "a": "Often"},
    ]

# ---------- Session State ----------
defaults = {"celeb_data": None, "q_index": 0, "score": 0, "pool": [], "answered": False}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

st.title("🎤 Celeb Scoop ∞ 💗 Jennie Mode")
st.caption("Search any idol/celebrity → bio + pics + unlimited quiz + Kpop beats")

celeb_name = st.text_input("🔍 Search Idol/Celeb", placeholder="Jennie BLACKPINK, Lisa, Jimin BTS, IU, Cardi B, Burna Boy")

if celeb_name and (not st.session_state.celeb_data or st.session_state.celeb_data["name"].lower()!= celeb_name.lower()):
    with st.spinner(f"Loading {celeb_name}... like Jennie’s intro 💋"):
        st.session_state.celeb_data = get_celeb_data(celeb_name.strip())
        st.session_state.pool = question_pool(st.session_state.celeb_data)
        random.shuffle(st.session_state.pool)
        st.session_state.q_index = 0
        st.session_state.score = 0
        st.session_state.answered = False
        st.rerun()

tabs = st.tabs(["💗 Bio + Pics", "♾️ Unlimited Quiz"])

# Tab 1: Bio + gallery
with tabs[0]:
    if st.session_state.celeb_data:
        d = st.session_state.celeb_data
        st.header(f"✨ {d['name']} ✨")
        if d["images"]:
            cols = st.columns(min(4, len(d["images"])))
            for i, url in enumerate(d["images"][:8]):
                with cols[i % len(cols)]:
                    st.image(url, use_container_width=True)
        else:
            st.image("https://via.placeholder.com/800x1000/ff7eb3/ffffff?text=No+Image", use_container_width=True)
        st.markdown("---")
        st.subheader("Full Bio")
        st.write(d["bio"] if d["bio"] else "No bio available")
        if d["url"]:
            st.markdown(f"[📖 Source]({d['url']})")
    else:
        st.info("Type a name above. Try: Jennie BLACKPINK for full Jennie Mode")

# Tab 2: Infinite quiz
with tabs[1]:
    if st.session_state.celeb_data:
        # refill pool when exhausted = infinite
        if st.session_state.q_index >= len(st.session_state.pool):
            st.session_state.pool = question_pool(st.session_state.celeb_data)
            random.shuffle(st.session_state.pool)
            st.session_state.q_index = 0

        q = st.session_state.pool[st.session_state.q_index]
        st.metric("Score", st.session_state.score)
        st.subheader(f"Q {st.session_state.q_index + 1} ♾️")

        choice = st.radio(q["q"], random.sample(q["opts"], len(q["opts"])), key=f"uq{st.session_state.q_index}", index=None)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Submit 💋", disabled=st.session_state.answered or not choice, use_container_width=True):
                st.session_state.answered = True
                if choice == q["a"]:
                    st.session_state.score += 1
                    st.success("✅ Correct! Jennie would be proud")
                else:
                    st.error(f"❌ Correct: {q['a']}")
        with col2:
            if st.button("Next →", disabled=not st.session_state.answered, use_container_width=True):
                st.session_state.q_index += 1
                st.session_state.answered = False
                st.rerun()
    else:
        st.info("Search a celeb first, then quiz unlocks ∞")

st.caption("💗 Pink theme + Kpop beat = Jennie energy. 0 API keys. Streamlit Cloud safe.")