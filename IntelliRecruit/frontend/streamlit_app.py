# -*- coding: utf-8 -*-
"""
Application Streamlit multipage — page d'accueil.

Design harmonisé avec le Module C (Amen Allah) via frontend/theme.py.
Lancer :  streamlit run frontend/streamlit_app.py
(l'API FastAPI doit tourner : cd backend ; uvicorn app.main:app --reload)
"""
import requests
import streamlit as st

from theme import appliquer_theme, carte_metrique, hero

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="IntelliRecruit", page_icon="📄", layout="wide")
appliquer_theme()

hero(
    "📄 IntelliRecruit",
    "Module A — CV Intelligence Engine · Stagiaire : Iheb Khaldi",
)

# --- Comment ça marche (3 étapes) ---
st.markdown(
    """
<div class="card">
<h3 style="margin-top:0; color:#1A1A2E;">Comment ça marche</h3>
<div style="display:flex; gap:30px; flex-wrap:wrap; margin-top:15px;">
  <div style="flex:1; min-width:180px; text-align:center;">
    <div style="font-size:36px; margin-bottom:8px;">1</div>
    <b>Déposez vos CVs</b>
    <p style="font-size:14px; color:#666; margin-top:5px;">PDF, DOCX ou TXT — jusqu'à plusieurs fichiers en simultané</p>
  </div>
  <div style="flex:1; min-width:180px; text-align:center;">
    <div style="font-size:36px; margin-bottom:8px;">2</div>
    <b>Extraction automatique</b>
    <p style="font-size:14px; color:#666; margin-top:5px;">Le moteur identifie les informations clés : identité, expériences, compétences</p>
  </div>
  <div style="flex:1; min-width:180px; text-align:center;">
    <div style="font-size:36px; margin-bottom:8px;">3</div>
    <b>Résultats structurés</b>
    <p style="font-size:14px; color:#666; margin-top:5px;">Consultez les profils extraits, les statistiques et les métriques de qualité</p>
  </div>
</div>
</div>
""",
    unsafe_allow_html=True,
)

# --- Chiffres clés ---
col1, col2, col3, col4 = st.columns(4)
with col1:
    carte_metrique("Formats supportés", "3")
with col2:
    carte_metrique("Champs extraits", "9")
with col3:
    carte_metrique("Precision O2", "100%")
with col4:
    carte_metrique("Langues", "FR / EN")

# Vérification que l'API répond (gestion d'erreur propre)
try:
    r = requests.get(f"{API_URL}/health", timeout=2)
    if r.status_code == 200:
        st.success("✅ API FastAPI connectée")
    else:
        st.error(f"L'API répond avec le code {r.status_code}")
except requests.exceptions.RequestException:
    st.error("❌ API injoignable. Lance-la : `cd backend ; uvicorn app.main:app --reload`")
