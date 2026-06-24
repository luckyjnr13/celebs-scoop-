import streamlit as st
import requests, random
from datetime import datetime
import urllib.parse

st.set_page_config(page_title="Celeb Scoop 🎤", page_icon="🎤", layout="wide")

# ---------- K-pop UI ----------
st.markdown("""
<style>
.stApp {background: linear-gradient(135deg, #ff9a9e 0%, #fad0c4 50%, #a18cd1 100%); color: #1a1a1a;}
h1,h2,h3,h4,.stMarkdown,.stText,label,p {color: #1a1a1a!important; font-family: 'Segoe UI', sans-serif;}
.stTabs [aria-selected="true"] {background: linear-gradient(90deg, #ff6ec4, #7873f5); color: white!important; font-weight: 700; border-radius: 12px;}
.stButton>button {background: linear-gradient(90deg, #ff6ec4, #7873f5); color: white; border: none; border-radius: 12px; font-weight: 600;}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.subheader("🎵 K-pop Vibes")
    if st.checkbox("Play background music", value=True):
        st.audio("https://cdn.pixabay.com/download/audio/2023/05/09/audio_c8c8a73467.mp3?filename=kpop-179923.mp3", format="audio/mp3", loop=True)
        st.caption("Tap ▶ once. Mobile blocks autoplay")

HEADERS = {"User-Agent": "CelebScoop/1.0 https://streamlit.io"}

# ---------- Source 1: Wikipedia REST API ----------
@st.cache_data(ttl=3600)
def get_wikipedia(name):
    """Get bio + image from Wikipedia. No key needed."""
    title = urllib.parse.quote(name.replace(" ", "_"))
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{title}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10).json()
        if r.get("type") == "disambiguation" or r.get("title") == "Not found.":
            return None
        bio = r.get("extract", "")
        img = r.get("original", {}).get("source") or r.get("thumbnail", {}).get("source", "")
        images = [img] if img else []
        return {"name": r.get("title", name), "bio": bio, "images": images, "url": r.get("content_urls",{}).get("desktop",{}).get("page","")}
    except:
        return None

# ---------- Source 2: Last.fm fallback for musicians/idols ----------
@st.cache_data(ttl=3600)
def get_lastfm(name):
    """Last.fm artist.getInfo - no API key required for basic info"""
    url = f"http://ws.audioscrobbler.com/2.0/?method=artist.getinfo&artist={urllib.parse.quote(name)}&format=json"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10).json()
        if "error" in r:
            return None
        artist = r.get("artist", {})
        bio = artist.get("bio", {}).get("summary", "").split("<a href")[0].strip()
        images = [img["#text"] for img in artist.get("image", []) if img["#text"] and img["size"] in ["extralarge", "mega"]]
        return {"name": artist.get("name", name), "bio": bio, "images": images[:4], "url": artist.get("url", "")}
    except:
        return None

def get_celeb_data(name):
    """Wikipedia first, Last.fm fallback. Combines images if both have them."""
    wiki = get_wikipedia(name)
    lastfm = get_lastfm(name)

    if wiki and wiki["bio"] and len(wiki["bio"]) > 50:
        # merge pics if lastfm has more
        imgs = wiki["images"][:]
        if lastfm:
            imgs += [u for u in lastfm["images"] if u not in imgs]
        wiki["images"] = imgs[:5]
        return wiki

    if lastfm and lastfm["bio"]:
        return lastfm

    return {"name": name, "bio": "No data found. Try full name like 'Jimin BTS' or 'Lisa BLACKPINK'", "images": [], "url": ""}

# ---------- State ----------
if "data" not in st.session_state:
    st.session_state.data = None

st.title("🎤 Celeb Scoop - Wikipedia + Last.fm")
st.caption("0 API keys. Wikipedia first, Last.fm fallback for Kpop/idols. Full bio + multiple pics")

col1, col2 = st.columns([4,1])
with col1:
    celeb = st.text_input("🔍 Search Celebrity/Idol", placeholder="Jimin BTS, Lisa BLACKPINK, IU, Cardi B, Burna Boy, Zendaya")
    if st.button("Scoop It! ✨", use_container_width=True) and celeb.strip():
        with st.spinner(f"Scooping {celeb}..."):
            st.session_state.data = get_celeb_data(celeb.strip())
with col2:
    st.metric("Last Scoop", datetime.now().strftime("%H:%M"))

tabs = st.tabs(["ℹ️ Bio + Pics", "🎯 Quiz"])

# Tab 1: Bio + gallery
with tabs[0]:
    if st.session_state.data:
        d = st.session_state.data
        st.header(d["name"])

        if d["images"]:
            cols = st.columns(min(3, len(d["images"])))
            for i, url in enumerate(d["images"][:6]):
                with cols[i % len(cols)]:
                    st.image(url, use_container_width=True)
        else:
            st.image("https://via.placeholder.com/800x1000?text=No+Image", use_container_width=True)

        st.markdown("---")
        st.subheader("Full Bio")
        st.write(d["bio"] if d["bio"] else "No bio available")
        if d["url"]:
            st.markdown(f"[📖 Source link]({d['url']})")
    else:
        st.info("Try: Jimin BTS, Lisa BLACKPINK, IU, NewJeans, Cardi B, Burna Boy...")

# Tab 2: Quick quiz
with tabs[1]:
    if st.session_state.data:
        name = st.session_state.data["name"]
        quiz = [
            {"q": f"Is {name} a public figure/entertainer?", "opts": ["Yes","No","Maybe","Unknown"], "a": "Yes"},
            {"q": f"Can you find info about {name} online?", "opts": ["Yes","No","Sometimes","Never"], "a": "Yes"},
            {"q": f"Best way to support {name}?", "opts": ["Stream/Watch their work","Ignore","Spam","Report"], "a": "Stream/Watch their work"},
            {"q": f"Where would you see {name} perform?", "opts": ["Concert/Stage","Oil rig","Farm","Lab"], "a": "Concert/Stage"},
        ]
        random.shuffle(quiz)
        ans = {}
        for i,q in enumerate(quiz):
            ans[i] = st.radio(q["q"], q["opts"], key=f"q{i}", index=None)

        if st.button("Check Quiz ✅", use_container_width=True):
            score = sum(1 for i,q in enumerate(quiz) if ans.get(i)==q["a"])
            for i,q in enumerate(quiz):
                if ans.get(i)==q["a"]:
                    st.success(f"Q{i+1}: ✅ Correct")
                else:
                    st.error(f"Q{i+1}: ❌ Correct: {q['a']}")
            st.balloons()
            st.success(f"Score: {score}/{len(quiz)} 🎉")
    else:
        st.info("Search a celeb above first")