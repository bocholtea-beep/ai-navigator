import streamlit as st
import google.generativeai as genai
import json
import os

# --- 1. GRUNDEINSTELLUNGEN ---
st.set_page_config(page_title="KI-Lern-Navigator", layout="wide", page_icon="🎓")

# Ein bisschen Design, damit es professionell aussieht
st.markdown("""
    <style>
    .stAlert { border-radius: 10px; }
    .stVideo { border-radius: 15px; overflow: hidden; }
    .tutor-box { background-color: #f0f2f6; padding: 20px; border-radius: 10px; border-left: 5px solid #007bff; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATEN LADEN ---
def load_content():
    """Lädt die Kursinhalte aus der content.json Datei"""
    try:
        with open('content.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("❌ Fehler: Die Datei 'content.json' wurde nicht gefunden. Bitte erstelle sie auf GitHub.")
        return None
    except json.JSONDecodeError:
        st.error("❌ Fehler: Die 'content.json' enthält einen Schreibfehler (Format falsch).")
        return None

content = load_content()

# --- 3. SEITENLEISTE (Navigation & Key) ---
with st.sidebar:
    st.title("🎓 Lern-Einstellungen")
    
    # API-Key Logik
    st.subheader("🔑 Verbindung")
    api_key = os.getenv("GOOGLE_API_KEY") # Versucht den Key aus den Cloud-Secrets zu lesen
    
    if not api_key:
        api_key = st.text_input("Gemini API-Key hier einfügen:", type="password")
    
    if api_key:
        genai.configure(api_key=api_key)
        st.success("✅ KI-Verbindung bereit!")
    else:
        st.warning("⚠️ Bitte gib einen API-Key ein, um den Tutor zu nutzen.")
        st.info("Einen Key bekommst du kostenlos auf: https://aistudio.google.com/")

    st.divider()

    # Lektionswahl
    if content and "micro_learnings" in content:
        titles = [m['title'] for m in content['micro_learnings']]
        selected_title = st.selectbox("Wähle deine Lektion:", titles)
        ml = next(m for m in content['micro_learnings'] if m['title'] == selected_title)
    else:
        ml = None

# --- 4. HAUPTBEREICH ---
if ml:
    st.title(f"Modul: {ml['title']}")
    
    col_links, col_rechts = st.columns([2, 1])

    # LINKE SEITE: Video & Infos
    with col_links:
        st.video(ml['video_url'])
        
        with st.expander("📖 Zusammenfassung der wichtigsten Punkte", expanded=True):
            for point in ml['summary_points']:
                st.write(f"✅ {point}")

    # RECHTE SEITE: KI-Tutor & Flashcards
    with col_rechts:
        st.subheader("🤖 Dein KI-Tutor")
        
        # Chat-Eingabe
        user_query = st.text_input("Hast du eine Frage zum Video?", placeholder="Frag mich etwas...")
        
        if user_query:
            if not api_key:
                st.error("Zuerst API-Key in der Sidebar eingeben!")
            else:
                with st.spinner("Tutor überlegt..."):
                    try:
                        # Wir probieren erst das schnelle Modell
                        model = genai.GenerativeModel('gemini-1.5-flash')
                        
                        # Wir geben der KI Kontext, damit sie weiß, worum es geht
                        kontext = f"Du bist ein Tutor. Das Thema ist: {ml['title']}. Wichtige Punkte: {', '.join(ml['summary_points'])}. {ml['system_prompt']}"
                        
                        antwort = model.generate_content(f"{kontext}\n\nFrage des Nutzers: {user_query}")
                        st.markdown(f"<div class='tutor-box'>{antwort.text}</div>", unsafe_allow_html=True)
                        
                    except Exception as e:
                        # Falls das nicht klappt, versuchen wir das alte Standard-Modell
                        try:
                            model_alt = genai.GenerativeModel('gemini-pro')
                            antwort_alt = model_alt.generate_content(user_query)
                            st.markdown(f"<div class='tutor-box'>{antwort_alt.text}</div>", unsafe_allow_html=True)
                        except Exception as e_final:
                            st.error(f"KI-Fehler: {str(e_final)}")

        st.divider()
        
        # Flashcards (Lernkarten)
        st.subheader("🗂️ Quiz-Karten")
        if 'card_idx' not in st.session_state: st.session_state.card_idx = 0
        if 'show_ans' not in st.session_state: st.session_state.show_ans = False
        
        cards = ml['flashcards']
        aktuelle_karte = cards[st.session_state.card_idx]
        
        # Anzeige der Karte
        if st.session_state.show_ans:
            st.success(f"**Antwort:**\n\n{aktuelle_karte['back']}")
        else:
            st.info(f"**Frage:**\n\n{aktuelle_karte['front']}")
        
        c1, c2 = st.columns(2)
        if c1.button("🔄 Umdrehen"):
            st.session_state.show_ans = not st.session_state.show_ans
            st.rerun()
            
        if c2.button("➡️ Nächste"):
            st.session_state.card_idx = (st.session_state.card_idx + 1) % len(cards)
            st.session_state.show_ans = False
            st.rerun()

else:
    st.warning("Bitte stelle sicher, dass eine gültige 'content.json' Datei vorhanden ist.")
