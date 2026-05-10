import streamlit as st
import google.generativeai as genai
import json
import os

# --- 1. DESIGN-TURBO (CSS) ---
st.set_page_config(page_title="KI Lern-Navigator", layout="wide", page_icon="🎓")

st.markdown("""
    <style>
    /* Hintergrund und Schrift */
    .stApp { background-color: #f8f9fc; }
    
    /* Karten-Design für Boxen */
    div.stChatMessage, div.stAlert, .st-emotion-cache-1r6slb0 {
        border-radius: 20px !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    
    /* Buttons wie App-Elemente */
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 3.5rem;
        background-color: #ffffff;
        color: #007bff;
        border: 2px solid #007bff;
        font-weight: bold;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #007bff;
        color: white;
    }
    
    /* Tutor-Antwort Box */
    .tutor-response {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 15px;
        border-left: 6px solid #007bff;
        margin-bottom: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    /* Überschriften-Styling */
    h1, h2, h3 { color: #1e293b; font-family: 'Inter', sans-serif; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. FUNKTIONEN ---
def get_ki_response(user_query, system_context, api_key):
    try:
        genai.configure(api_key=api_key)
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        selected = 'models/gemini-1.5-flash' if 'models/gemini-1.5-flash' in models else models[0]
        model = genai.GenerativeModel(selected)
        response = model.generate_content(f"{system_context}\n\nFrage: {user_query}")
        return response.text
    except Exception as e:
        return f"KI-Fehler: {str(e)}"

def load_data():
    try:
        with open('content.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except: return None

# --- 3. DATEN & SIDEBAR ---
data = load_data()
with st.sidebar:
    st.markdown("## ⚙️ Einstellungen")
    api_key = os.getenv("GOOGLE_API_KEY") or st.text_input("Dein API-Key:", type="password")
    st.divider()
    if data:
        titles = [m['title'] for m in data['micro_learnings']]
        choice = st.selectbox("Lektion auswählen:", titles)
        ml = next(m for m in data['micro_learnings'] if m['title'] == choice)
    else:
        st.error("content.json fehlt!")
        ml = None

# --- 4. HAUPTBEREICH (MOBILE OPTIMIERT) ---
if ml:
    st.title(f"🎓 {ml['title']}")
    
    # Videobereich oben (nimmt volle Breite auf Handy ein)
    st.video(ml['video_url'])
    
    tab1, tab2, tab3 = st.tabs(["📝 Info", "🤖 Tutor", "🗂️ Quiz"])
    
    with tab1:
        st.subheader("Wichtigste Punkte")
        for p in ml['summary_points']:
            st.markdown(f"✅ {p}")
            
    with tab2:
        st.subheader("Frag deinen Tutor")
        frage = st.text_input("Was möchtest du wissen?", placeholder="Schreib hier...")
        if frage:
            if api_key:
                with st.spinner("Tutor denkt nach..."):
                    antwort = get_ki_response(frage, ml['system_prompt'], api_key)
                    st.markdown(f"<div class='tutor-response'>{antwort}</div>", unsafe_allow_html=True)
            else:
                st.warning("Bitte API-Key in der Sidebar eingeben.")

    with tab3:
        st.subheader("Wissen prüfen")
        if 'c_idx' not in st.session_state: st.session_state.c_idx = 0
        if 'flipped' not in st.session_state: st.session_state.flipped = False
        
        cards = ml['flashcards']
        card = cards[st.session_state.c_idx]
        
        # Karte anzeigen
        display = card['back'] if st.session_state.flipped else card['front']
        color = "#e7f3ff" if not st.session_state.flipped else "#f0fff4"
        
        st.markdown(f"""
            <div style="background-color: {color}; padding: 30px; border-radius: 20px; text-align: center; min-height: 150px; display: flex; align-items: center; justify-content: center; border: 1px solid #d1d5db; margin-bottom: 20px;">
                <h3 style="margin: 0;">{display}</h3>
            </div>
        """, unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        if c1.button("🔄 Umdrehen"):
            st.session_state.flipped = not st.session_state.flipped
            st.rerun()
        if c2.button("➡️ Nächste"):
            st.session_state.c_idx = (st.session_state.c_idx + 1) % len(cards)
            st.session_state.flipped = False
            st.rerun()
