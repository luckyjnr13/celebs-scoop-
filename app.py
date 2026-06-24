import streamlit as st
import requests
import random

# 1. Page Config
st.set_page_config(
    page_title="Celebs Scoop",
    page_icon="✨",
    layout="centered"
)

# 2. Universal Glamorous Styling
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #11111d 0%, #2a1b40 100%);
        color: #ffffff;
    }
    /* Tab formatting */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        justify-content: center;
    }
    .stTabs [data-baseweb="tab"] {
        font-size: 18px;
        font-weight: bold;
        color: #aaa;
        padding: 10px 20px;
    }
    .stTabs [aria-selected="true"] {
        color: #f1c40f !important;
        border-bottom-color: #f1c40f !important;
    }
    /* Buttons custom styling */
    div.stButton > button {
        background: linear-gradient(45deg, #ff416c, #ff4b2b) !important;
        color: white !important;
        font-size: 16px !important;
        font-weight: bold !important;
        border-radius: 15px !important;
        border: none !important;
        padding: 10px 20px !important;
        box-shadow: 0 4px 15px rgba(255, 75, 43, 0.3);
        transition: all 0.3s ease;
    }
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(255, 75, 43, 0.5);
    }
    h1 {
        text-align: center;
        background: -webkit-linear-gradient(#f39c12, #f1c40f);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }
    .news-card { background: rgba(255,255,255,0.07); padding: 15px; border-radius: 10px; margin-bottom: 15px; border-left: 4px solid #f1c40f; }
    </style>
    """, unsafe_allow_html=True)

st.title("✨ CELEBS SCOOP ✨")

# 3. Create the Beautiful Separated Tabs
tab_home, tab_search, tab_quiz = st.tabs(["🏠 Welcome", "🔍 Search Scoop", "🧠 Unlimited Quiz"])

# ==========================================
# TAB 1: WELCOME HOME
# ==========================================
with tab_home:
    st.write("")
    st.markdown("""
    ### Welcome to the Hollywood Insider Portal! 🎬
    Get real-time biographic data from Wikipedia and the absolute latest press breaks via NewsAPI—all inside one beautiful interface.
    
    Use the navigation menu tabs at the top to flip screens!
    """)
    st.image("https://images.unsplash.com/photo-1514306191717-452ec28c7814?q=80&w=600", caption="Step onto the Red Carpet")

# ==========================================
# TAB 2: LIVE CELEBRITY SEARCH
# ==========================================
with tab_search:
    st.header("🔍 Search Live Celebrity Details")
    st.write("Fetch direct bio profiles and the last 30 days of global press records instantly.")
    
    def get_wiki_bio(celeb_name):
        url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + celeb_name.replace(" ", "_")
        try:
            response = requests.get(url, headers={"User-Agent": "CelebScoopApp/1.0"})
            if response.status_code == 200:
                data = response.json()
                return {
                    "summary": data.get("extract", "No bio outline found."),
                    "image": data.get("thumbnail", {}).get("source", None)
                }
        except: pass
        return None

    def get_live_news(celeb_name, api_key):
        url = f"https://newsapi.org/v2/everything?q={celeb_name}&sortBy=publishedAt&language=en&pageSize=4&apiKey={api_key}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response.json().get("articles", [])
        except: pass
        return []

    search_query = st.text_input("Enter a celebrity's full name:", key="search_bar", placeholder="e.g., Zendaya, Tom Holland, Taylor Swift")
    
    if search_query:
        st.write("---")
        with st.spinner("Gathering Hollywood intel..."):
            wiki_data = get_wiki_bio(search_query)
            if wiki_data:
                col1, col2 = st.columns([1, 2])
                with col1:
                    if wiki_data["image"]:
                        st.image(wiki_data["image"], use_container_width=True)
                    else:
                        st.info("📷 No public imagery profile found.")
                with col2:
                    st.subheader(search_query.title())
                    st.write(wiki_data["summary"])
            else:
                st.warning("Could not automatically retrieve a Wikipedia summary for this name.")

            st.write("---")
            st.subheader("📰 Live Press Headlines")
            
            if "news_api" in st.secrets and st.secrets["news_api"]["key"]:
                articles = get_live_news(search_query, st.secrets["news_api"]["key"])
                if articles:
                    for art in articles:
                        st.markdown(f"""
                        <div class="news-card">
                            <h4 style="margin:0;"><a href="{art['url']}" target="_blank" style="color: #ff4b4b; text-decoration:none;">{art['title']}</a></h4>
                            <p style="font-size:12px; color:#aaa; margin:5px 0;">Source: {art['source']['name']}</p>
                            <p style="font-size:14px; margin:0;">{art['description'] or 'No description summary available.'}</p>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No fresh articles found for this name in the past month.")
            else:
                st.info("💡 NewsAPI Configuration missing. Attach your key in Streamlit settings to see live headlines.")

# ==========================================
# TAB 3: UNLIMITED QUIZ
# ==========================================
with tab_quiz:
    st.header("🧠 Unlimited Celebrity Trivia")
    
    quiz_pool = [
        {"q": "Who won the Album of the Year for 'Midnights' at the Grammys?", "choices": ["Billie Eilish", "Taylor Swift", "SZA", "Olivia Rodrigo"], "ans": "Taylor Swift"},
        {"q": "What is the name of Rihanna's makeup brand?", "choices": ["Kylie Cosmetics", "Rare Beauty", "Fenty Beauty", "Haus Labs"], "ans": "Fenty Beauty"},
        {"q": "Which actor played J. Robert Oppenheimer in the 2023 biographical hit film?", "choices": ["Cillian Murphy", "Robert Downey Jr.", "Matt Damon", "Tom Hardy"], "ans": "Cillian Murphy"},
        {"q": "How many times did Ross Geller get divorced on 'Friends'?", "choices": ["1", "2", "3", "4"], "ans": "3"},
        {"q": "Which artist wore a dress made of raw meat to the 2010 MTV Video Music Awards?", "choices": ["Katy Perry", "Lady Gaga", "Nicki Minaj", "Rihanna"], "ans": "Lady Gaga"}
    ]

    # Initialize persistent variables
    if 'score' not in st.session_state:
        st.session_state.score = 0
    if 'current_q' not in st.session_state:
        st.session_state.current_q = random.choice(quiz_pool)

    # Simple Layout metrics
    col_score, col_reset = st.columns([3, 1])
    col_score.markdown(f"### 🏆 Current Score: `{st.session_state.score}`")
    if col_reset.button("Reset Score 🔄"):
        st.session_state.score = 0
        st.rerun()

    st.write("---")
    st.markdown(f"#### **Question:** {st.session_state.current_q['q']}")
    
    # Render answers
    for choice in st.session_state.current_q["choices"]:
        if st.button(choice, key=f"btn_{choice}"):
            if choice == st.session_state.current_q["ans"]:
                st.success("🎉 Correct choice! +1 Point!")
                st.session_state.score += 1
            else:
                st.error(f"❌ Incorrect! The correct answer was **{st.session_state.current_q['ans']}**.")
            
            # Immediately queue up another question choice
            st.session_state.current_q = random.choice(quiz_pool)
            st.button("Next Question ➡️", key="next_q")
