import streamlit as st
import requests

st.set_page_config(page_title="Search - Celebs Scoop", page_icon="🔍")

# Global style matching
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #0f2027, #203a43, #2c5364); color: white; }
    h1, h2, h3 { color: #f1c40f !important; }
    .news-card { background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🔍 Search Live Celebrity Scoop")

# Dynamic helper functions
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
    except Exception:
        pass
    return None

def get_live_news(celeb_name, api_key):
    url = f"https://newsapi.org/v2/everything?q={celeb_name}&sortBy=publishedAt&language=en&pageSize=5&apiKey={api_key}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json().get("articles", [])
    except Exception:
        pass
    return []

# User input
search_query = st.text_input("Enter a celebrity's full name:", placeholder="e.g., Zendaya, Tom Holland, Taylor Swift")

if search_query:
    st.write("---")
    
    with st.spinner(f"Gathering intel on {search_query}..."):
        # 1. Fetch from Wikipedia
        wiki_data = get_wiki_bio(search_query)
        
        if wiki_data:
            col1, col2 = st.columns([1, 2])
            with col1:
                if wiki_data["image"]:
                    st.image(wiki_data["image"], use_container_width=True)
                else:
                    st.write("📷 No public profile image found.")
            with col2:
                st.header(search_query.title())
                st.write(wiki_data["summary"])
        else:
            st.warning("Could not automatically retrieve a Wikipedia summary for this name.")

        st.write("---")
        st.subheader("📰 Live Press & Headlines")
        
        # 2. Fetch from NewsAPI using Streamlit Secrets
        if "news_api" in st.secrets and st.secrets["news_api"]["key"]:
            api_key = st.secrets["news_api"]["key"]
            articles = get_live_news(search_query, api_key)
            
            if articles:
                for art in articles:
                    st.markdown(f"""
                    <div class="news-card">
                        <h4><a href="{art['url']}" target="_blank" style="color: #ff4b4b; text-decoration:none;">{art['title']}</a></h4>
                        <p style="font-size:13px; color:#ccc;">Source: {art['source']['name']} | Published: {art['publishedAt'][:10]}</p>
                        <p style="font-size:14px;">{art['description'] or 'No description provided.'}</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No recent headlines found for this person in the last 30 days.")
        else:
            st.info("💡 NewsAPI Key config missing. Add your NewsAPI key to your Streamlit secrets to display live global tracking items.")
