# -*- coding: utf-8 -*-
"""Tests S4 — A4 : normalisation des skills (ontologie + fuzzy matching)."""
from app.services.cv_intelligence.skills_normalizer import normaliser_skill
from app.services.cv_intelligence.skills_extractor import (
    extraire_skills_cv,
    extraire_skills_texte,
    parser_section_skills,
)


# ---------- normalisation exacte ----------
def test_normaliser_variantes_python():
    """Exigence du cahier : 'Python 3', 'python', 'Python programming' -> 'python'."""
    assert normaliser_skill("Python 3") == ("python", "language")
    assert normaliser_skill("python") == ("python", "language")
    assert normaliser_skill("Python programming") == ("python", "language")


def test_normaliser_numero_version():
    assert normaliser_skill("Python 3.11") == ("python", "language")


def test_normaliser_alias():
    assert normaliser_skill("sklearn") == ("scikit-learn", "framework")
    assert normaliser_skill("k8s") == ("kubernetes", "cloud")
    assert normaliser_skill("postgres") == ("postgresql", "database")


def test_normaliser_categories_cahier():
    """Les 5 catégories demandées : langages, frameworks, cloud, BDD, méthodo."""
    assert normaliser_skill("Java")[1] == "language"
    assert normaliser_skill("Django")[1] == "framework"
    assert normaliser_skill("AWS")[1] == "cloud"
    assert normaliser_skill("MongoDB")[1] == "database"
    assert normaliser_skill("Scrum")[1] == "methodology"


# ---------- fuzzy matching ----------
def test_fuzzy_faute_de_frappe():
    assert normaliser_skill("postgress") == ("postgresql", "database")
    assert normaliser_skill("javascrip") == ("javascript", "language")


def test_skill_inconnu():
    assert normaliser_skill("basket-ball") is None
    assert normaliser_skill("") is None


# ---------- extraction dans le texte libre ----------
def test_frontieres_de_mots():
    """'javascript' ne doit PAS matcher 'java' (piège classique)."""
    skills = extraire_skills_texte("Développement javascript côté client.")
    assert "javascript" in skills
    assert "java" not in skills


def test_caracteres_speciaux():
    skills = extraire_skills_texte("Maîtrise de C++ et de Power BI.")
    assert "c++" in skills
    assert "power bi" in skills


def test_alias_ambigus_ignores_en_texte_libre():
    """'R' seul dans une phrase ne doit pas devenir un skill (trop ambigu)."""
    assert "r" not in extraire_skills_texte("Voir la lettre R du dictionnaire.")


def test_dedup_alias_chevauchants():
    """« SQL Server » ne doit PAS produire aussi 'sql' (fix précision S7)."""
    skills = extraire_skills_texte("Expérience sur SQL Server et SSIS.")
    assert "sql server" in skills
    assert "sql" not in skills


def test_sql_seul_reste_detecte():
    """Mais 'SQL' seul (sans 'Server') reste bien détecté."""
    assert "sql" in extraire_skills_texte("Bonne maîtrise du SQL et des index.")


# ---------- section Compétences ----------
def test_parser_section_avec_ambigus():
    """Dans la section Compétences, 'R' et 'C' sont acceptés (contexte clair)."""
    skills = parser_section_skills("Python, R, C, SQL Server")
    noms = [s.name for s in skills]
    assert noms == ["python", "r", "c", "sql server"]


def test_parser_section_deduplique():
    skills = parser_section_skills("Python, python 3, Python Programming")
    assert [s.name for s in skills] == ["python"]


# ---------- combinaison des sources (précision : titres exclus) ----------
def test_skill_dans_titre_de_poste_non_extrait():
    """Un skill présent SEULEMENT dans un intitulé de poste ne doit pas
    devenir une compétence déclarée (fix précision : évite « Ingénieur
    Machine Learning » -> 'machine learning')."""
    noms = [
        s.name
        for s in extraire_skills_cv(
            "Python, SQL",  # section Compétences
            descriptions_experience=["Analyse de données clients."],
        )
    ]
    assert "machine learning" not in noms  # jamais déclaré
    assert "python" in noms and "sql" in noms


def test_skill_dans_description_experience_extrait():
    """Un skill réellement cité dans une description d'expérience est bien
    ajouté à la liste, même absent de la section Compétences."""
    noms = [
        s.name
        for s in extraire_skills_cv(
            "Python",  # section Compétences (react absent)
            descriptions_experience=["Développement d'une interface en React."],
        )
    ]
    assert "python" in noms
    assert "react" in noms
