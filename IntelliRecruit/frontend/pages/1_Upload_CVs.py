# -*- coding: utf-8 -*-
"""
S3 — Page Upload CVs : la vitrine de la brique de parsing basique.

Nouveautés S3 : upload PDF + DOCX + TXT, affichage de l'identité extraite
(nom, email, téléphone...) au format CVData, langue détectée.
Toujours là : multipage, session_state, form, barre de progression (F2).
"""
import pathlib
import sys

import requests
import streamlit as st

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from theme import appliquer_theme, hero

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Upload CVs", page_icon="⬆️", layout="wide")
appliquer_theme()
hero("⬆️ Upload CVs", "Dépose tes CVs (PDF, DOCX, TXT) → CVData structuré")

# session_state : les résultats survivent aux interactions de la page
if "cvs_parses" not in st.session_state:
    st.session_state.cvs_parses = []  # liste de dicts CVParseResponse

# form : tout est soumis d'un coup au clic sur le bouton
with st.form("upload_form"):
    fichiers = st.file_uploader(
        "Dépose tes CVs (PDF, DOCX ou TXT) — plusieurs fichiers possibles",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True,
    )
    soumettre = st.form_submit_button("🚀 Parser")

if soumettre and fichiers:
    barre = st.progress(0, text="Parsing en cours...")  # exigence F2
    for i, f in enumerate(fichiers):
        try:
            r = requests.post(
                f"{API_URL}/api/cv/parse",
                files={"file": (f.name, f.getvalue())},
                timeout=120,
            )
            if r.status_code == 200:
                st.session_state.cvs_parses.append(r.json())
            else:
                st.error(f"{f.name} : erreur {r.status_code} — {r.json().get('detail')}")
        except requests.exceptions.RequestException as e:
            st.error(f"{f.name} : API injoignable ({e})")
        barre.progress((i + 1) / len(fichiers), text=f"{i + 1}/{len(fichiers)} CV(s) traité(s)")
    st.success("Terminé ✅")

# Affichage du dernier CV parsé
if st.session_state.cvs_parses:
    dernier = st.session_state.cvs_parses[-1]
    identite = dernier["identity"]

    st.subheader(f"Dernier CV parsé : {dernier['filename']}")
    st.caption(
        f"id : `{dernier['id']}` · format : **{dernier['format']}** · "
        f"langue détectée : **{dernier['language'] or '?'}** · "
        f"{dernier['nb_caracteres']} caractères"
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Prénom", identite["first_name"] or "—")
        st.metric("Nom", identite["last_name"] or "—")
    with col2:
        st.metric("Email", identite["email"] or "—")
        st.metric("Téléphone", identite["phone"] or "—")
    with col3:
        st.metric("Localisation", identite["location"] or "—")
        if identite["linkedin"]:
            st.markdown(f"**LinkedIn** : [{identite['linkedin']}]({identite['linkedin']})")
        else:
            st.metric("LinkedIn", "—")

    st.divider()

    # --- Nouveau en S4 : les sections structurées du CVData ---
    colg, cold = st.columns(2)

    with colg:
        st.markdown("### 💼 Expériences")
        if dernier["experience"]:
            for exp in dernier["experience"]:
                fin = exp["end_date"] or "présent"
                st.markdown(f"**{exp['title']}** — {exp['company']}")
                st.caption(f"{exp['start_date'] or '?'} → {fin}")
                if exp["description"]:
                    st.write(exp["description"])
                if exp["skills"]:
                    st.caption("Skills : " + ", ".join(exp["skills"]))
        else:
            st.write("—")

        st.markdown("### 🎓 Formations")
        if dernier["education"]:
            for edu in dernier["education"]:
                annees = f"{edu['start_year'] or '?'} - {edu['end_year'] or '?'}"
                st.markdown(f"**{edu['degree'] or '?'}** — {edu['school']}")
                spec = f" · {edu['field']}" if edu["field"] else ""
                st.caption(f"{annees}{spec}")
        else:
            st.write("—")

    with cold:
        st.markdown("### 🛠️ Compétences (normalisées)")
        if dernier["skills"]:
            # regroupées par catégorie (langages / frameworks / cloud...)
            par_cat: dict = {}
            for s in dernier["skills"]:
                par_cat.setdefault(s["category"], []).append(s["name"])
            for cat, noms in par_cat.items():
                st.markdown(f"**{cat}** : {', '.join(noms)}")
        else:
            st.write("—")

        st.markdown("### 🗣️ Langues")
        if dernier["languages"]:
            for lang in dernier["languages"]:
                niveau = f" ({lang['level']})" if lang["level"] else ""
                st.markdown(f"- {lang['name']}{niveau}")
        else:
            st.write("—")

        st.markdown("### 📜 Certifications")
        if dernier["certifications"]:
            for cert in dernier["certifications"]:
                st.markdown(f"- {cert}")
        else:
            st.write("—")

    with st.expander("🔍 JSON CVData complet (contrat du trinôme)"):
        st.json(dernier)
