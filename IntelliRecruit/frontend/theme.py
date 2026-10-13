# -*- coding: utf-8 -*-
"""
Thème visuel partagé de l'application IntelliRecruit.

Reprend le design défini par Amen Allah (Module C) — police Inter, fond clair
#F5F7FC, accent violet #5B4CF0, hero en dégradé, cartes blanches arrondies —
pour que TOUTES les pages (Module A comprises) aient la même identité visuelle.

Usage dans une page :
    from theme import appliquer_theme, hero
    st.set_page_config(...)     # doit rester la 1re commande Streamlit
    appliquer_theme()
    hero("Titre", "sous-titre")
"""
import streamlit as st

# Palette (source unique de vérité pour les couleurs)
VIOLET = "#5B4CF0"
VIOLET_CLAIR = "#8D84FF"
FOND = "#F5F7FC"

_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

html, body, [class*="css"]{ font-family:'Inter', sans-serif; }

.stApp{ background:#F5F7FC; }

/* Couleurs de texte : SOMBRE par défaut pour rester lisible sur le fond clair.
   (Sans ça, en mode sombre Streamlit met le texte en blanc -> invisible.) */
.stApp, .block-container,
h1, h2, h3, h4, h5, h6,
p, li, span, label, td, th,
.stMarkdown, .stCaption, [data-testid="stMetricValue"],
[data-testid="stMetricLabel"]{ color:#1A1A2E; }

/* Le hero et les boutons gardent leur texte BLANC (sur fond violet) */
.hero, .hero *{ color:#ffffff !important; }
.stButton>button, .stButton>button *{ color:#ffffff !important; }

/* Les cartes chiffres gardent leurs couleurs propres */
.metric-value{ color:#5B4CF0 !important; }
.metric-title{ color:#777 !important; }

/* on masque le menu Streamlit par défaut pour un rendu "produit" */
#MainMenu {visibility:hidden;}
footer {visibility:hidden;}

.block-container{ padding-top:2rem; padding-left:3rem; padding-right:3rem; }

/* Hero (bandeau de titre) */
.hero{
    background:linear-gradient(135deg,#5B4CF0,#8D84FF);
    padding:35px; border-radius:22px; color:white; margin-bottom:30px;
    box-shadow:0 12px 35px rgba(91,76,240,.25);
}
.hero h1{ margin:0; font-size:40px; font-weight:800; }
.hero p{ margin-top:10px; font-size:17px; opacity:.9; }

/* Cartes */
.card{
    background:white; border-radius:20px; padding:24px; border:1px solid #ECECF5;
    box-shadow:0 8px 25px rgba(0,0,0,.05); margin-bottom:20px; transition:.3s;
}
.card:hover{ transform:translateY(-3px); box-shadow:0 12px 30px rgba(0,0,0,.08); }

/* Carte métrique (chiffre clé) */
.metric-card{
    background:white; border-radius:18px; padding:20px; text-align:center;
    border:1px solid #ECECF5; box-shadow:0 6px 20px rgba(0,0,0,.05);
}
.metric-title{ color:#777; font-size:15px; font-weight:600; }
.metric-value{ font-size:34px; font-weight:800; color:#5B4CF0; margin-top:8px; }

/* Boutons */
.stButton>button{
    width:100%; border:none; border-radius:12px;
    background:linear-gradient(90deg,#5B4CF0,#786CFF); color:white;
    font-weight:700; padding:.65rem; transition:.3s;
}
.stButton>button:hover{
    transform:translateY(-2px); box-shadow:0 10px 20px rgba(91,76,240,.35);
}

/* Inputs arrondis */
.stTextInput input,
.stSelectbox div[data-baseweb="select"]{ border-radius:12px; }

hr{ margin-top:2rem; margin-bottom:2rem; }
</style>
"""


def appliquer_theme() -> None:
    """Injecte le CSS commun. À appeler après st.set_page_config()."""
    st.markdown(_CSS, unsafe_allow_html=True)


def hero(titre: str, sous_titre: str = "") -> None:
    """Affiche le bandeau de titre en dégradé violet."""
    st.markdown(
        f'<div class="hero"><h1>{titre}</h1>'
        f'<p>{sous_titre}</p></div>',
        unsafe_allow_html=True,
    )


def carte_metrique(titre: str, valeur: str) -> None:
    """Affiche un chiffre clé dans une carte blanche (style Module C)."""
    st.markdown(
        f'<div class="metric-card"><div class="metric-title">{titre}</div>'
        f'<div class="metric-value">{valeur}</div></div>',
        unsafe_allow_html=True,
    )
