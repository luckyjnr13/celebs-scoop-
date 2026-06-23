import streamlit as st
import random

st.set_page_config(page_title="Quiz - Celebs Scoop", page_icon="🧠")

st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #4158D0 0%, #C850C0 46%, #FFCC70 100%); color: white; }
    div.stButton > button { width: 100%; font-size: 18px !important; margin-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🧠 Unlimited Celeb Trivia")

quiz_pool = [
    {"q": "Who won the Album of the Year for 'Midnights' at the Grammys?", "choices": ["Billie Eilish", "Taylor Swift", "SZA", "Olivia Rodrigo"], "ans": "Taylor Swift"},
    {"q": "What is the name of Rihanna's makeup brand?", "choices": ["Kylie Cosmetics", "Rare Beauty", "Fenty Beauty", "Haus Labs"], "ans": "Fenty Beauty"},
    {"q": "Which actor played J. Robert Oppenheimer in Christopher Nolan's 2023 film?", "choices": ["Cillian Murphy", "Robert Downey Jr.", "Matt Damon", "Tom Hardy"], "ans": "Cillian Murphy"},
    {"q": "How many times did Ross Geller get divorced on 'Friends'?", "choices": ["1", "2", "3", "4"], "ans": "3"},
    {"q": "Which artist wore a dress made of raw meat to the 2010 MTV Video Music Awards?", "choices": ["Katy Perry", "Lady Gaga", "Nicki Minaj", "Rihanna"], "ans": "Lady Gaga"}
]

if 'score' not in st.session_state:
    st.session_state.score = 0
if 'current_q' not in st.session_state:
    st.session_state.current_q = random.choice(quiz_pool)

st.sidebar.metric(label="🏆 Total Score", value=st.session_state.score)

st.subheader("Question:")
st.write(st.session_state.current_q["q"])

# Choices layout
for choice in st.session_state.current_q["choices"]:
    if st.button(choice, key=choice):
        if choice == st.session_state.current_q["ans"]:
            st.success("🎉 Correct! +1 Point!")
            st.session_state.score += 1
        else:
            st.error(f"❌ Incorrect! The right answer was **{st.session_state.current_q['ans']}**.")
        
        # Pull a new question instantly
        st.session_state.current_q = random.choice(quiz_pool)
        st.button("Next Question ➡️")
        
if st.button("Reset Score 🔄", key="reset"):
    st.session_state.score = 0
    st.rerun()
