# -*- coding: utf-8 -*-
"""
S6 — Page Métriques : precision / recall du parser affichés visuellement.

Appelle l'endpoint GET /api/cv/metrics (qui évalue le parser sur le dataset
annoté) et affiche le rapport par champ + l'objectif O2 du cahier des charges.
"""
import pathlib
import sys

import pandas as pd
import requests
import streamlit as st

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from theme import appliquer_theme, carte_metrique, hero

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Métriques", page_icon="📈", layout="wide")
appliquer_theme()
hero("📈 Métriques du parser", "Precision / recall du Module A sur le dataset annoté")

try:
    r = requests.get(f"{API_URL}/api/cv/metrics", timeout=60)
except requests.exceptions.RequestException:
    st.error("❌ API injoignable. Lance-la : `cd backend ; uvicorn app.main:app --reload`")
    st.stop()

if r.status_code != 200:
    st.error(f"Erreur {r.status_code} : {r.json().get('detail')}")
    st.stop()

data = r.json()
o2 = data["objectif_o2"]
par_champ = data["par_champ"]

# --- Objectif O2 (nom + email + skills) : cartes chiffres clés (style Module C) ---
st.subheader(f"🎯 Objectif O2 (nom + email + skills) — sur {data['nb_cvs']} CVs annotés")
atteint = o2["precision"] >= 0.85
col1, col2, col3 = st.columns(3)
with col1:
    carte_metrique("Precision (cible ≥ 85%)", f"{o2['precision']:.0%}")
with col2:
    carte_metrique("Recall", f"{o2['recall']:.0%}")
with col3:
    carte_metrique("F1", f"{o2['f1']:.2f}")
st.write("")
if atteint:
    st.success("✅ Objectif O2 atteint (precision ≥ 85%)")
else:
    st.warning("⚠️ Objectif O2 non atteint — precision < 85%")

st.divider()

# --- Tableau + graphique par champ ---
df = pd.DataFrame(
    [
        {
            "champ": champ,
            "precision": m["precision"],
            "recall": m["recall"],
            "F1": m["f1"],
            "faux positifs": m["fp"],
            "valeurs ratées": m["fn"],
        }
        for champ, m in par_champ.items()
    ]
).set_index("champ")

st.subheader("Détail par champ")
st.dataframe(
    df.style.format({"precision": "{:.0%}", "recall": "{:.0%}", "F1": "{:.2f}"}),
    use_container_width=True,
)

st.subheader("Precision par champ")
st.bar_chart(df["precision"])

# --- Points à améliorer ---
a_ameliorer = df[(df["faux positifs"] + df["valeurs ratées"]) > 0]
if not a_ameliorer.empty:
    st.subheader("🔧 Champs à améliorer")
    for champ, row in a_ameliorer.iterrows():
        st.write(
            f"- **{champ}** : {int(row['faux positifs'])} faux positifs, "
            f"{int(row['valeurs ratées'])} valeurs ratées"
        )

_cible = "✅ exigence cahier §5.1 atteinte (100+)" if data["nb_cvs"] >= 100 else "à étendre vers 100+"
st.caption(f"Dataset : {data['nb_cvs']} CVs annotés (data/ground_truth.json) — {_cible}.")
