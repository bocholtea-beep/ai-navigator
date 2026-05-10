import streamlit as st
import google.generativeai as genai
import json
import os

# --- 1. GRUNDEINSTELLUNGEN ---
st.set_page_config(page_title="KI-Lern-Navigator", layout="wide", page_icon="🎓")

# Design-Anpassungen
st.markdown("""
    <style>
    .stAlert { border-radius: 10px; }
    .tutor-box { 
        background-color: #f8f9fa; 
        padding: 15px; 
        border-radius: 10px; 
        border-left: 5px solid #007bff;
        color: #1a1a1a;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATEN LADEN ---
def load_content():
    try:
        with open('content.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None

content = load_content()

# --- 3. SIDEBAR (Navigation & API-Key) ---
with st.sidebar:
    st.title("⚙️ Einstellungen")
    
    # API-Key Logik: Priorität auf Secrets, sonst Eingabefeld
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        api_key = st.text_input("Gemini API-Key:", type="password", help="Hole deinen Key auf aistudio.google.com")
    
    if api_key:
        genai.configure(api_key=api_key)
        st.success("✅ Verbindung aktiv")
    else:
        st.warning("⚠️ Bitte API-Key eintragen.")

    st.divider()

    if content and "micro_learnings" in content:
        titles = [m['title'] for m in content['micro_learnings']]
        selected_title = st.selectbox("Lektion wählen:", titles)
        ml = next(m for m in content['micro_learnings'] if m['title'] == selected_title)
    else:
        st.error("Datei 'content.json' fehlt oder ist leer.")
        ml = None

# --- 4. HAUPTBEREICH ---
if ml:
    st.title(f"📖 {ml['title']}")
    
    col_links, col_rechts = st.columns([2, 1])

    # LINKS: Video und Zusammenfassung
    with col_links:
        st.video(ml['video_url'])
        st.subheader("Zusammenfassung")
        for point in ml['summary_points']:
            st.write(f"• {point}")

    # RECHTS: KI-Tutor und Flashcards
    with col_rechts:
        st.subheader("🤖 KI-Tutor")
        user_query = st.text_input("Frage zum Inhalt:", placeholder="Tippe hier deine Frage...")
        
        if user_query:
            if not api_key:
                st.error("API-Key fehlt!")
            else:
                with st.spinner("Tutor antwortet..."):
                    try:
                        # Hauptversuch mit dem aktuellsten Modell
                        model = genai.GenerativeModel('gemini-1.5-flash')
                        kontext = f"Du bist ein hilfreicher Tutor. Thema: {ml['title']}. {ml['system_prompt']}"
                        
                        response = model.generate_content(f"{kontext}\n\nFrage: {user_query}")
                        st.markdown(f"<div class='tutor-box'>{response.text}</div>", unsafe_allow_html=True)
                    
                    except Exception as e:
                        # Backup: Falls Flash ein Problem hat, versuche Pro 1.5
                        try:
                            model_pro = genai.GenerativeModel('gemini-1.5-pro')
                            response = model_pro.generate_content(user_query)
                            st.info(response.text)
                        except Exception as e_final:
                            st.error("Fehler bei der KI-Verbindung.")
                            st.write(f"Details: {str(e_final)}")

        st.divider()
        
        # Flashcards
        st.subheader("🗂️ Lernkarten")
        if 'c_idx' not in st.session_state: st.session_state.c_idx = 0
        if 'flipped' not in st.session_state: st.session_state.flipped = False
        
        card = ml['flashcards'][st.session_state.c_idx]
        anzeige = card['back'] if st.session_state.flipped else card['front']
        
        st.info(f"**{anzeige}**")
        
        c1, c2 = st.columns(2)
        if c1.button("🔄 Drehen"):
            st.session_state.flipped = not st.session_state.flipped
            st.rerun()
        if c2.button("➡️ Nächste"):
            st.session_state.c_idx = (st.session_state.c_idx + 1) % len(ml['flashcards'])
            st.session_state.flipped = False
            st.rerun()
else:
    st.info("Warte auf Konfiguration...")
