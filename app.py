import streamlit as st
import google.generativeai as genai
import json
import os

# --- 1. SETUP ---
st.set_page_config(page_title="KI-Lern-Navigator", layout="wide")

# --- 2. DATEN LADEN ---
def load_content():
    try:
        with open('content.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None

content = load_content()

# --- 3. SIDEBAR ---
with st.sidebar:
    st.title("⚙️ Einstellungen")
    api_key = os.getenv("GOOGLE_API_KEY") or st.text_input("Gemini API-Key:", type="password")
    
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
        ml = None

# --- 4. HAUPTBEREICH ---
if ml:
    st.title(f"📖 {ml['title']}")
    col_links, col_rechts = st.columns([2, 1])

    with col_links:
        st.video(ml['video_url'])
        st.subheader("Zusammenfassung")
        for point in ml['summary_points']:
            st.write(f"• {point}")

    with col_rechts:
        st.subheader("🤖 KI-Tutor")
        user_query = st.text_input("Frage zum Inhalt:", key="query_input")
        
        if user_query and api_key:
            with st.spinner("Tutor sucht passendes Modell..."):
                try:
                    # SCHRITT 1: Wir suchen, welches Modell dein Key darf
                    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                    
                    # SCHRITT 2: Wir wählen ein verfügbares Modell (bevorzugt 1.5-flash)
                    selected_model = 'models/gemini-1.5-flash' 
                    if selected_model not in available_models:
                        selected_model = available_models[0] # Nimm das erste verfügbare
                    
                    # SCHRITT 3: Antwort generieren
                    model = genai.GenerativeModel(selected_model)
                    response = model.generate_content(f"{ml['system_prompt']}\n\nFrage: {user_query}")
                    st.info(response.text)
                    
                except Exception as e:
                    st.error("Kein Zugriff auf KI-Modelle möglich.")
                    st.write(f"Fehler-Details: {str(e)}")
                    st.info("Tipp: Erstelle im Google AI Studio einen NEUEN Key in einem NEUEN Projekt.")

        st.divider()
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
