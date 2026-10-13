# -*- coding: utf-8 -*-
"""Tests S4 — A3 : structuration hiérarchique (sections + items)."""
from app.services.cv_intelligence.section_detector import (
    decouper_sections,
    detecter_section,
)
from app.services.cv_intelligence.experience_parser import (
    extraire_plage_dates,
    parser_experiences,
)
from app.services.cv_intelligence.education_parser import parser_formations
from app.services.cv_intelligence.languages_parser import (
    parser_certifications,
    parser_langues,
)

CV_STRUCTURE = """AMIRA BEN SALEM
Ariana, Tunisie

COMPÉTENCES CLÉS
Python, SQL, Power BI

EXPÉRIENCE PROFESSIONNELLE
Stage Data Analyst — Vermeg (Juin 2025 - Août 2025)
Analyse des données clients avec Python et Power BI.

FORMATION
Ingénieur Informatique, spécialité Data & IA — ESPRIT (2022 - 2025)

LANGUES
Arabe (natif), Français (courant), Anglais (B2)

CERTIFICATIONS
Microsoft Power BI Data Analyst (PL-300)
"""


# ---------- détection des en-têtes ----------
def test_detecter_section_fr():
    assert detecter_section("COMPÉTENCES CLÉS") == "skills"
    assert detecter_section("EXPÉRIENCE PROFESSIONNELLE") == "experience"
    assert detecter_section("Formation") == "education"
    assert detecter_section("Langues :") == "languages"


def test_detecter_section_en():
    assert detecter_section("WORK EXPERIENCE") == "experience"
    assert detecter_section("Skills") == "skills"
    assert detecter_section("EDUCATION") == "education"


def test_detecter_section_ligne_normale():
    assert detecter_section("Analyse des données clients") is None
    assert detecter_section("") is None


def test_decouper_sections_complet():
    blocs = decouper_sections(CV_STRUCTURE)
    assert "AMIRA BEN SALEM" in blocs["entete"]
    assert "Python, SQL" in blocs["skills"]
    assert "Vermeg" in blocs["experience"]
    assert "ESPRIT" in blocs["education"]
    assert "Arabe" in blocs["languages"]
    assert "PL-300" in blocs["certifications"]


# ---------- plages de dates ----------
def test_plage_mois_annee():
    debut, fin, _ = extraire_plage_dates("Stage (Juin 2025 - Août 2025)")
    assert debut == "2025-06"
    assert fin == "2025-08"


def test_plage_annees_seules():
    debut, fin, _ = extraire_plage_dates("Backend Developer (2021 - 2024)")
    assert debut == "2021"
    assert fin == "2024"


def test_plage_poste_actuel():
    """Convention J10 : end_date = None pour le poste actuel."""
    _, fin, _ = extraire_plage_dates("Dev — X (Janvier 2023 - présent)")
    assert fin is None
    _, fin_en, _ = extraire_plage_dates("ML Engineer (2022 - present)")
    assert fin_en is None


def test_plage_forme_de_a():
    """'de Juin 2025 à Août 2025' (sans parenthèses ni tiret)."""
    debut, fin, _ = extraire_plage_dates("Stage chez Vermeg de Juin 2025 à Août 2025.")
    assert debut == "2025-06"
    assert fin == "2025-08"


def test_pas_de_plage():
    assert extraire_plage_dates("Analyse des données clients.") is None


# ---------- expériences ----------
def test_parser_experiences_complet():
    bloc = (
        "Stage Data Analyst — Vermeg (Juin 2025 - Août 2025)\n"
        "Analyse des ventes avec Python et Power BI.\n"
        "\n"
        "Développeur Web chez TunisAI (Janvier 2023 - présent)\n"
        "Plateforme SaaS en React."
    )
    items = parser_experiences(bloc)
    assert len(items) == 2
    assert items[0].title == "Stage Data Analyst"
    assert items[0].company == "Vermeg"
    assert items[0].start_date == "2025-06"
    assert items[0].end_date == "2025-08"
    assert "Analyse des ventes" in items[0].description
    assert "python" in items[0].skills          # A4 branché sur A3
    assert "power bi" in items[0].skills
    assert items[1].company == "TunisAI"
    assert items[1].end_date is None            # poste actuel
    assert "react" in items[1].skills


def test_parser_experiences_separateur_at():
    items = parser_experiences("Backend Developer at FinTech Ltd (2021 - 2024)")
    assert items[0].title == "Backend Developer"
    assert items[0].company == "FinTech Ltd"


# ---------- formations ----------
def test_parser_formation_avec_specialite():
    items = parser_formations(
        "Ingénieur Informatique, spécialité Data & IA — ESPRIT (2022 - 2025)"
    )
    assert len(items) == 1
    assert items[0].degree == "Ingénieur Informatique"
    assert items[0].field == "Data & IA"
    assert items[0].school == "ESPRIT"
    assert items[0].start_year == 2022
    assert items[0].end_year == 2025


def test_parser_formation_virgule_anglaise():
    items = parser_formations("BSc Computer Science, University of Manchester (2017 - 2020)")
    assert items[0].degree == "BSc Computer Science"
    assert items[0].school == "University of Manchester"


def test_parser_formation_ecole_en_premier():
    """Si l'école est écrite AVANT le diplôme, on remet dans le bon ordre."""
    items = parser_formations("Université de Tunis — Master BI (2021 - 2023)")
    assert items[0].school == "Université de Tunis"
    assert items[0].degree == "Master BI"


# ---------- langues ----------
def test_parser_langues_niveaux_normalises():
    langues = parser_langues("Arabe (natif), Français (courant), Anglais (B2)")
    assert [(l.name, l.level) for l in langues] == [
        ("arabic", "native"), ("french", "fluent"), ("english", "B2"),
    ]


def test_parser_langues_sans_niveau():
    langues = parser_langues("Arabe, Français, Anglais")
    assert [l.level for l in langues] == [None, None, None]


def test_parser_langues_ignore_le_bruit():
    """Un mot qui n'est pas une langue ne doit pas devenir une langue."""
    assert parser_langues("Python et communication") == []


# ---------- certifications ----------
def test_parser_certifications():
    certifs = parser_certifications(
        "Microsoft Power BI Data Analyst (PL-300)\nAWS Certified Solutions Architect"
    )
    assert certifs == [
        "Microsoft Power BI Data Analyst (PL-300)",
        "AWS Certified Solutions Architect",
    ]
