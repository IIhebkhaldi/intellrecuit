# -*- coding: utf-8 -*-
"""
Service de parsing — réutilise la logique corrigée de la Semaine 1 (J3 + J4).

Pipeline : PDF -> texte brut -> nettoyage -> NER spaCy filtré + regex + heuristiques.
C'est l'embryon du futur cv_intelligence_service.py (Semaine 3).
"""
import io
import re
import uuid

from pypdf import PdfReader

# ------------------------------------------------------------------
# Chargement paresseux de spaCy (une seule fois, au premier appel)
# ------------------------------------------------------------------
_nlp = None

def get_nlp():
    global _nlp
    if _nlp is None:
        import spacy
        _nlp = spacy.load("fr_core_news_sm")
    return _nlp


# ------------------------------------------------------------------
# 1) Extraction du texte d'un PDF (depuis des bytes -> pratique pour l'API)
# ------------------------------------------------------------------
def extraire_texte_pdf(contenu: bytes) -> str:
    """Extrait tout le texte d'un PDF reçu en bytes (upload FastAPI)."""
    try:
        reader = PdfReader(io.BytesIO(contenu))
        return "".join(page.extract_text() or "" for page in reader.pages)
    except Exception as e:
        raise ValueError(f"Impossible de lire le PDF : {e}")


# ------------------------------------------------------------------
# 2) Nettoyage (bruit des polices d'icônes — voir S1/J4)
# ------------------------------------------------------------------
ICONES_PDF = [
    r"♂¶ap-¶arker-alt", r"♂phone-alt", r"/envel.?pe",
    r"/linkedin", r"/github", r"[♂¶⌢#ï§]",
]

def nettoyer_texte(text: str) -> str:
    for pat in ICONES_PDF:
        text = re.sub(pat, " ", text, flags=re.IGNORECASE)
    return re.sub(r"[ \t]+", " ", text)


# ------------------------------------------------------------------
# 3) Filtres anti-bruit (S1/J4)
# ------------------------------------------------------------------
SECTIONS_CV = {
    "résumé", "resume", "compétences", "competences", "clés",
    "expérience", "experience", "professionnelle", "formation",
    "éducation", "education", "projets", "projet", "langues",
    "certifications", "contact", "licence", "baccalauréat", "stage",
}
LANGUES_PARLEES = {"arabe", "français", "francais", "anglais",
                   "english", "french", "arabic", "natif"}
COMPETENCES_TECH = {
    "python", "sql", "java", "javascript", "c", "c#", "c++", "r", "php", "jee",
    "scikit-learn", "tensorflow", "keras", "pandas", "numpy", "matplotlib",
    "seaborn", "beautifulsoup", "power bi", "power query", "dax", "tableau",
    "excel", "ssas", "ssis", "ssms", "mysql", "sql server", "postgresql",
    "mongodb", "oracle", "odoo", "microsoft dynamics 365", "django", "talend",
    "régression", "regression", "classification", "clustering",
    "feature engineering", "machine learning", "deep learning",
    "data warehousing", "data warehouse", "etl", "kpi", "nlp", "erp", "crm",
    "spacy", "fastapi", "docker", "git", "gitlab", "streamlit", "crisp-dm",
    "business intelligence", "data analysis", "data science",
    "linkedin", "github",
}
MOTS_ECOLE = {"lycée", "lycee", "institut", "école", "ecole", "université",
              "universite", "faculté", "faculte", "esprit", "iset"}


def _mots(t: str):
    return [m for m in re.split(r"[\s,;:–\-]+", t.lower()) if m]


def est_bruit(texte: str) -> bool:
    t = re.sub(r"\s+", " ", texte.strip().lower())
    if len(t) < 2 or len(t) > 60:
        return True
    if any(ch.isdigit() for ch in t):
        return True
    if any(sym in t for sym in ["@", "|", "/", "•", "&"]):
        return True
    if re.search(r"\b(d|l|qu|j|n|s|c)[’']\s*$", t):
        return True
    mots = _mots(t)
    if not mots:
        return True
    if mots[0] in SECTIONS_CV:
        return True
    if t in COMPETENCES_TECH or t in LANGUES_PARLEES:
        return True
    if all(m in SECTIONS_CV or m in COMPETENCES_TECH or m in LANGUES_PARLEES
           for m in mots):
        return True
    return False


def est_ecole(texte: str) -> bool:
    mots = _mots(texte)
    return bool(mots) and mots[0] in MOTS_ECOLE


def dedupe(liste):
    vus, res = set(), []
    for x in liste:
        x = re.sub(r"\s+", " ", str(x).strip())
        if x and x.lower() not in vus:
            vus.add(x.lower())
            res.append(x)
    return res


# ------------------------------------------------------------------
# 4) Regex : emails, téléphones, dates (S1/J4)
# ------------------------------------------------------------------
def extraire_emails(text: str):
    return dedupe(re.findall(r"\b[\w\.\-]+@[\w\.\-]+\.\w{2,}\b", text))


def extraire_telephones(text: str):
    pattern = r"(?<!\d)(?:\+216[\s\.\-]?)?\d{2}[\s\.\-]?\d{3}[\s\.\-]?\d{3}(?!\d)"
    return dedupe(re.findall(pattern, text))


MOIS = (r"(?:janvier|février|fevrier|mars|avril|mai|juin|juillet|"
        r"août|aout|septembre|octobre|novembre|décembre|decembre|"
        r"janv\.?|fév\.?|fevr?\.?|avr\.?|juil\.?|sept\.?|oct\.?|nov\.?|déc\.?|dec\.?)")


def extraire_dates(text: str):
    dates, reste = [], text
    patterns_plages = [
        rf"{MOIS}\s+(?:19|20)\d{{2}}\s*[–\-—]\s*(?:{MOIS}\s+)?(?:19|20)\d{{2}}",
        r"(?:19|20)\d{2}\s*[–\-—]\s*(?:(?:19|20)\d{2}|présent|present)",
    ]
    for pat in patterns_plages:
        dates += re.findall(pat, reste, flags=re.IGNORECASE)
        reste = re.sub(pat, " ", reste, flags=re.IGNORECASE)
    for pat in [rf"{MOIS}\s+(?:19|20)\d{{2}}", r"\b(?:19|20)\d{2}\b"]:
        dates += re.findall(pat, reste, flags=re.IGNORECASE)
        reste = re.sub(pat, " ", reste, flags=re.IGNORECASE)
    return dedupe(dates)


def extraire_nom_candidat(text: str):
    for ligne in text.split("\n")[:5]:
        mots = ligne.strip().split()
        if 2 <= len(mots) <= 4 and all(re.fullmatch(r"[A-Za-zÀ-ÿ'\-]+", m) for m in mots):
            if not est_bruit(ligne):
                return ligne.strip().title()
    return None


# ------------------------------------------------------------------
# 5) Fonction principale (S1/J4, inchangée)
# ------------------------------------------------------------------
def extract_entities(text: str) -> dict:
    text = nettoyer_texte(text)
    doc = get_nlp()(text)
    entities = {"personnes": [], "organisations": [], "lieux": [],
                "dates": [], "emails": [], "telephones": []}
    for ent in doc.ents:
        if est_bruit(ent.text):
            continue
        if ent.label_ == "PER":
            entities["personnes"].append(ent.text)
        elif ent.label_ == "ORG" or est_ecole(ent.text):
            entities["organisations"].append(ent.text)
        elif ent.label_ == "LOC":
            entities["lieux"].append(ent.text)
    nom = extraire_nom_candidat(text)
    if nom:
        entities["personnes"].insert(0, nom)
    entities["emails"] = extraire_emails(text)
    entities["telephones"] = extraire_telephones(text)
    entities["dates"] = extraire_dates(text)
    for k in entities:
        entities[k] = dedupe(entities[k])
    return entities


def nouveau_cv_id() -> str:
    return f"cv_{uuid.uuid4().hex[:8]}"
