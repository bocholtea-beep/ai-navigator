import streamlit as st
import google.generativeai as genai
import json
import os

# 1. Seite konfigurieren
st.set_page_config(page_title="KI-Navigator", layout="wide")

# 2. Inhalte laden (content.json)
def load_content():
    try:
        with open('content.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        # Falls die Datei fehlt, erstellen wir ein leeres Grundgerüst
        return {"micro_learnings": []}

content = load_content()

# 3. Seitenleiste für Einstellungen
with st.sidebar:
    st.title("⚙️ Setup")
    # Sucht den Key in den Replit-Secrets oder lässt dich einen eintippen
    api_key = os.getenv("GOOGLE_API_KEY") or st.text_input("Gemini API-Key:", type="password")
    
    if api_key:
        genai.configure(api_key=api_key)
        st.success("API bereit!")
    
    st.divider()
    
    # Auswahl der Lektion
    if content and content['micro_learnings']:
        titles = [m['title'] for m in content['micro_learnings']]
        selected_title = st.selectbox("Wähle ein Modul:", titles)
        ml = next(m for m in content['micro_learnings'] if m['title'] == selected_title)
    else:
        st.error("Inhalte konnten nicht geladen werden.")
        ml = None

# 4. Hauptbereich der App
if ml:
    st.title(ml['title'])
    
    col1, col2 = st.columns([2, 1])

    with col1:
        # Video anzeigen
        st.video(ml['video_url'])
        
        # Zusammenfassung anzeigen
        st.subheader("📝 Zusammenfassung")
        for point in ml['summary_points']:
            st.write(f"• {point}")

    with col2:
        # KI-Tutor Chat
        st.subheader("🤖 KI-Tutor")
        user_input = st.text_input("Stelle eine Frage zum Video:")
        
        if user_input and api_key:
            # Sicherheits-Logik gegen den 'NotFound' Fehler
            try:
                # Versuch 1: Schnellstes Modell
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(f"{ml['system_prompt']}\n\nFrage: {user_input}")
                st.info(response.text)
            except Exception:
                try:
                    # Versuch 2: Stabileres Standard-Modell
                    model = genai.GenerativeModel('gemini-pro')
                    response = model.generate_content(f"{ml['system_prompt']}\n\nFrage: {user_input}")
                    st.info(response.text)
                except Exception as e:
                    st.error("Das KI-Modell konnte nicht erreicht werden. Prüfe deinen API-Key.")

        # Lernkarten (Flashcards)
        st.divider()
        st.subheader("🗂️ Quiz-Karten")
        if 'card_idx' not in st.session_state: st.session_state.card_idx = 0
        if 'flip' not in st.session_state: st.session_state.flip = False
        
        card = ml['flashcards'][st.session_state.card_idx]
        
        # Karte anzeigen
        text = card['back'] if st.session_state.flip else card['front']
        st.info(f"**{text}**")
        
        if st.button("Karte umdrehen"):
            st.session_state.flip = not st.session_state.flip
            st.rerun()
            
        if st.button("Nächste Karte"):
            st.session_state.card_idx = (st.session_state.card_idx + 1) % len(ml['flashcards'])
            st.session_state.flip = False
            st.rerun()
