import streamlit as st

st.set_page_config(
    page_title="Celebs Scoop",
    page_icon="✨",
    layout="centered"
)

# Shared Styling for Glamorous Dark Theme across pages
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #11111d 0%, #2a1b40 100%);
        color: #ffffff;
    }
    div.stButton > button:first-child {
        background: linear-gradient(45deg, #ff416c, #ff4b2b);
        color: white;
        font-size: 18px;
        font-weight: bold;
        border-radius: 20px;
        border: none;
        padding: 12px 30px;
        box-shadow: 0 4px 15px rgba(255, 75, 43, 0.4);
        transition: all 0.3s ease;
    }
    div.stButton > button:first-child:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(255, 75, 43, 0.6);
    }
    h1 {
        text-align: center;
        background: -webkit-linear-gradient(#f39c12, #f1c40f);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("✨ CELEBS SCOOP ✨")
st.write("---")

st.markdown("""
### Welcome to the Hollywood Insider Portal! 🎬
Get real-time biographic data from Wikipedia and the absolute latest press breaks via NewsAPI—all in one gorgeous app.

**Get started using the sidebar on the left:**
* 🔍 **Search:** Instantly uncover bio summaries and live news about any celebrity.
* 🧠 **Quiz:** Face our limitless trivia machine and maintain a high score!
""")

st.image("https://images.unsplash.com/photo-1514306191717-452ec28c7814?q=80&w=600", caption="Step onto the Red Carpet")
st.write("---")
st.markdown("### 🚀 Quick Navigation:")

try:
    st.page_link("pages/1_🔍_Search.py", label="Go to Celebrity Search", icon="🔍")
    st.page_link("pages/2_🧠_Quiz.py", label="Go to Unlimited Quiz", icon="🧠")
except Exception:
    st.info("👈 Please use the sidebar on the very left of your screen to change pages!")





