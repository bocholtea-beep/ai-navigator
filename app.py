import streamlit as st
import google.generativeai as genai
import json
import os

# --- 1. FUNKTIONEN (Die Werkzeuge) ---
def get_ki_response(user_query, system_context, api_key):
    try:
        genai.configure(api_key=api_key)
        # Findet automatisch ein funktionierendes Modell
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
    except:
        return None

# --- 2. SETUP & DATEN ---
st.set_page_config(page_title="KI-Navigator", layout="wide", page_icon="🎓")
data = load_data()

# --- 3. SIDEBAR ---
with st.sidebar:
    st.title("⚙️ Setup")
    api_key = os.getenv("GOOGLE_API_KEY") or st.text_input("API-Key:", type="password")
    st.divider()
    
    if data:
        titles = [m['title'] for m in data['micro_learnings']]
        choice = st.selectbox("Lektion wählen:", titles)
        ml = next(m for m in data['micro_learnings'] if m['title'] == choice)
    else:
        st.error("Datei 'content.json' nicht gefunden!")
        ml = None

# --- 4. HAUPTBEREICH ---
if ml:
    st.title(f"📖 {ml['title']}")
    col1, col2 = st.columns([2, 1])

    # Links: Video und Notizen
    with col1:
        st.video(ml['video_url'])
        with st.expander("📝 Zusammenfassung", expanded=True):
            for p in ml['summary_points']:
                st.write(f"• {p}")

    # Rechts: Tutor und Lernkarten
    with col2:
        # Teil A: Der Tutor
        st.subheader("🤖 KI-Tutor")
        frage = st.text_input("Deine Frage zum Video:", key="user_frage")
        if frage:
            if api_key:
                with st.spinner("Überlege..."):
                    st.info(get_ki_response(frage, ml['system_prompt'], api_key))
            else:
                st.warning("Bitte Key eingeben!")

        st.divider()

        # Teil B: Die Lernkarten (Flashcards)
        st.subheader("🗂️ Lernkarten")
        
        # Speicher für die aktuelle Karte
        if 'c_idx' not in st.session_state: st.session_state.c_idx = 0
        if 'flipped' not in st.session_state: st.session_state.flipped = False
        
        cards = ml['flashcards']
        aktuelle_karte = cards[st.session_state.c_idx]
        
        # Anzeige der Karte
        box_text = aktuelle_karte['back'] if st.session_state.flipped else aktuelle_karte['front']
        st.success(f"**{'Antwort' if st.session_state.flipped else 'Frage'}:**\n\n{box_text}")
        
        btn_col1, btn_col2 = st.columns(2)
        if btn_col1.button("🔄 Umdrehen"):
            st.session_state.flipped = not st.session_state.flipped
            st.rerun()
        
        if btn_col2.button("➡️ Nächste"):
            st.session_state.c_idx = (st.session_state.c_idx + 1) % len(cards)
            st.session_state.flipped = False
            st.rerun()
