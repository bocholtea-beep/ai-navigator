
import streamlit as st
import json
import google.generativeai as genai

# Page Config
st.set_page_config(page_title="AI Learning Navigator", layout="wide")

# UI Styling
st.markdown("""
    <style>
    .main { background-color: #050505; color: #f5f5f5; }
    .stButton>button { background-color: #deff9a; color: black; border-radius: 10px; font-weight: bold; border: none; width: 100%; }
    .card { background-color: #1a1a1a; padding: 20px; border-radius: 15px; border: 1px solid #deff9a; margin-bottom: 20px; }
    h1, h2, h3 { color: #deff9a !important; }
    .stExpander { border: 1px solid #333; background-color: #111; }
    </style>
""", unsafe_allow_html=True)

# SIDEBAR BYOK
with st.sidebar:
    st.title("⚙️ Setup")
    api_key = st.text_input("Gemini API-Key", type="password")
    if api_key:
        genai.configure(api_key=api_key)
        st.success("API verbunden")
    else:
        st.warning("Key erforderlich")

# LOAD CONTENT
def load_data():
    with open('content.json', 'r', encoding='utf-8') as f:
        return json.load(f)

data = load_data()

# MAIN GUI
st.title("🚀 AI Learning Navigator")

if api_key:
    selected_title = st.selectbox("Lerneinheit wählen:", [m['title'] for m in data['micro_learnings']])
    ml = next(m for m in data['micro_learnings'] if m['title'] == selected_title)

    tab1, tab2, tab3 = st.tabs(["📺 Training", "🃏 Karten", "🤖 Tutor"])

    with tab1:
        st.subheader(ml['title'])
        st.video(ml['video_url'])
        if st.button("Lernanalyse starten"):
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.write("### Top 10 Takeaways")
            for p in ml['summary_points']:
                st.write(f"- {p}")
            st.markdown("</div>", unsafe_allow_html=True)

    with tab3:
        if "chat" not in st.session_state: st.session_state.chat = []
        for msg in st.session_state.chat:
            with st.chat_message(msg["role"]): st.write(msg["content"])
        
        if p := st.chat_input("Frage den Tutor..."):
            st.session_state.chat.append({"role": "user", "content": p})
            with st.chat_message("user"): st.write(p)
            model = genai.GenerativeModel('gemini-1.5-flash')
            res = model.generate_content(f"{ml['system_prompt']}\n\nUser: {p}")
            st.session_state.chat.append({"role": "assistant", "content": res.text})
            with st.chat_message("assistant"): st.write(res.text)

    with tab2:
        cols = st.columns(2)
        for i, card in enumerate(ml['flashcards']):
            with cols[i % 2]:
                with st.expander(f"Karten-Vorderseite: {card['front']}"):
                    st.info(card['back'])
else:
    st.write("Bitte API-Key in der Seitenleiste eingeben.")
