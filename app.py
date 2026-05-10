import streamlit as st
import google.generativeai as genai
import json
import os

# --- FUNKTIONEN (Die Werkzeuge im Hintergrund) ---
def get_ki_response(user_query, system_context, api_key):
    """Kümmert sich um die KI-Suche, ohne das Hauptprogramm zu stören"""
    try:
        genai.configure(api_key=api_key)
        # Sucht automatisch das beste verfügbare Modell
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        selected = 'models/gemini-1.5-flash' if 'models/gemini-1.5-flash' in models else models[0]
        
        model = genai.GenerativeModel(selected)
        response = model.generate_content(f"{system_context}\n\nFrage: {user_query}")
        return response.text
    except Exception as e:
        return f"Fehler: {str(e)}"

def load_data():
    with open('content.json', 'r', encoding='utf-8') as f:
        return json.load(f)

# --- APP-LAYOUT ---
st.set_page_config(page_title="KI-Navigator", layout="wide")
data = load_data()

# Sidebar für das Setup
with st.sidebar:
    st.title("⚙️ Setup")
    # Sucht erst in der Umgebung (Secrets), dann im Textfeld
    api_key = os.getenv("GOOGLE_API_KEY") or st.text_input("API-Key:", type="password")
    st.divider()
    
    if data:
        titles = [m['title'] for m in data['micro_learnings']]
        choice = st.selectbox("Lektion:", titles)
        ml = next(m for m in data['micro_learnings'] if m['title'] == choice)

# Hauptbereich
if data and ml:
    st.title(ml['title'])
    col1, col2 = st.columns([2, 1])

    with col1:
        st.video(ml['video_url'])
        st.expander("Notizen", expanded=True).write(ml['summary_points'])

    with col2:
        st.subheader("🤖 Tutor")
        frage = st.text_input("Deine Frage:")
        if frage and api_key:
            with st.spinner("KI denkt nach..."):
                antwort = get_ki_response(frage, ml['system_prompt'], api_key)
                st.info(antwort)
