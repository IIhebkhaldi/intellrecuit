# -*- coding: utf-8 -*-
"""Page Résultats : récap du CVData structuré + top skills + gestion des CVs.

Chaque CV est supprimable **individuellement** (bouton par ligne). La suppression
appelle DELETE /api/cv/{id} côté serveur pour retirer aussi de la base, puis
retire l'entrée de la session Streamlit.
"""
import pathlib
import sys
from collections import Counter

import pandas as pd
import requests
import streamlit as st

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from theme import appliquer_theme, hero

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Résultats", page_icon="📊", layout="wide")
appliquer_theme()
hero("📊 Résultats de la session", "Récap des CVs parsés · suppression individuelle")

cvs_bruts = st.session_state.get("cvs_parses", [])

# Déduplication par id : un même CV re-uploadé revient avec le MÊME id (le
# backend déduplique par hash) -> évite deux lignes et surtout deux boutons
# avec la même clé (StreamlitDuplicateElementKey).
vus_ids: set = set()
cvs = []
for cv in cvs_bruts:
    if cv["id"] not in vus_ids:
        vus_ids.add(cv["id"])
        cvs.append(cv)
if len(cvs) != len(cvs_bruts):
    st.session_state.cvs_parses = cvs  # on nettoie la session au passage

if not cvs:
    st.info("Aucun CV parsé pour l'instant. Va sur la page **Upload CVs**.")
else:
    st.caption(f"{len(cvs)} CV(s) dans la session")

    # --- Tableau récap avec bouton Supprimer par ligne ---
    entete = st.columns([2, 1, 2, 2, 3, 1, 1, 1, 1, 1])
    for col, titre in zip(
        entete,
        ["fichier", "langue", "prénom", "nom", "email",
         "expé.", "form.", "skills", "langues", ""],
    ):
        col.markdown(f"**{titre}**")

    a_supprimer = None  # id du CV à supprimer (repéré après la boucle)
    for i, cv in enumerate(cvs):
        c = st.columns([2, 1, 2, 2, 3, 1, 1, 1, 1, 1])
        c[0].write(cv["filename"])
        c[1].write(cv["language"] or "?")
        c[2].write(cv["identity"]["first_name"] or "—")
        c[3].write(cv["identity"]["last_name"] or "—")
        c[4].write(cv["identity"]["email"] or "—")
        c[5].write(len(cv["experience"]))
        c[6].write(len(cv["education"]))
        c[7].write(len(cv["skills"]))
        c[8].write(len(cv["languages"]))
        # clé unique par LIGNE (index + id) -> jamais de collision de clé
        if c[9].button("🗑️", key=f"del_{i}_{cv['id']}", help="Supprimer ce CV"):
            a_supprimer = cv["id"]

    if a_supprimer:
        try:
            r = requests.delete(f"{API_URL}/api/cv/{a_supprimer}", timeout=10)
            if r.status_code in (204, 404):
                # 204 = supprimé côté DB ; 404 = pas en DB (déjà retiré) — on
                # nettoie la session dans les deux cas pour rester cohérent.
                st.session_state.cvs_parses = [
                    x for x in cvs if x["id"] != a_supprimer
                ]
                st.success("CV supprimé.")
                st.rerun()
            else:
                st.error(f"Erreur {r.status_code} : {r.json().get('detail')}")
        except requests.exceptions.RequestException as e:
            st.error(f"API injoignable ({e})")

    # --- Top skills du lot (préfigure le dashboard analytique Module C) ---
    compteur = Counter(s["name"] for cv in cvs for s in cv["skills"])
    if compteur:
        st.subheader("Top des compétences (tous CVs de la session)")
        top = pd.DataFrame(compteur.most_common(10), columns=["skill", "occurrences"])
        st.bar_chart(top.set_index("skill")["occurrences"])

    # --- Bouton "vider tout" AVEC confirmation (double clic) ---
    st.divider()
    if st.session_state.get("confirmer_vider"):
        st.warning(f"⚠️ Supprimer les **{len(cvs)}** CV(s) de la session ?")
        col_ok, col_annuler = st.columns(2)
        if col_ok.button("Oui, tout supprimer"):
            for cv in cvs:
                try:
                    requests.delete(f"{API_URL}/api/cv/{cv['id']}", timeout=10)
                except requests.exceptions.RequestException:
                    pass  # on continue même si un DELETE échoue
            st.session_state.cvs_parses = []
            st.session_state.confirmer_vider = False
            st.rerun()
        if col_annuler.button("Annuler"):
            st.session_state.confirmer_vider = False
            st.rerun()
    else:
        if st.button("🗑️ Vider toute la session"):
            st.session_state.confirmer_vider = True
            st.rerun()
