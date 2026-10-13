# -*- coding: utf-8 -*-
"""
A2 — NER spaCy avancé (Semaine 4).

Exigences du cahier des charges (§5.1) :
- spaCy avec modèle français / anglais (choisi selon la langue détectée en A1)
- Extraction : personnes, organisations, lieux, dates, emails, téléphones
  (emails/téléphones/dates restent en regex — plus fiables que le NER pour ça,
  c'est la logique S1 réutilisée)

Rôle dans le pipeline S4 : les ORGANISATIONS servent de filet de sécurité
quand la structuration (A3) n'a pas trouvé l'entreprise d'une expérience.

Le custom NER entraîné pour les compétences techniques est remplacé en S4
par l'ontologie + fuzzy matching (A4) : l'entraînement viendra avec le
dataset annoté de la S6.
"""
from typing import Optional

from app.services import parsing

# Cache des modèles chargés : {"fr": nlp_fr, "en": nlp_en}
_MODELES: dict[str, object] = {}
_NOMS_MODELES = {"fr": "fr_core_news_sm", "en": "en_core_web_sm"}


def get_nlp(langue: Optional[str]):
    """Charge (une seule fois) le modèle spaCy de la langue du CV.

    Fallback en cascade : langue inconnue ou modèle non installé -> français
    (le modèle en_core_web_sm s'installe avec :
    python -m spacy download en_core_web_sm).
    """
    code = langue if langue in _NOMS_MODELES else "fr"
    if code not in _MODELES:
        import spacy
        try:
            _MODELES[code] = spacy.load(_NOMS_MODELES[code])
        except OSError:
            # modèle non téléchargé : on retombe sur le français (toujours là)
            _MODELES[code] = parsing.get_nlp()
    return _MODELES[code]


def extraire_entites_avancees(texte: str, langue: Optional[str] = "fr") -> dict:
    """NER multi-langue + filtres anti-bruit S1 + regex fiables.

    Retourne le même format que parsing.extract_entities (S1/S2) mais avec
    le bon modèle selon la langue du CV.
    """
    texte = parsing.nettoyer_texte(texte)
    doc = get_nlp(langue)(texte)

    # labels : le modèle fr dit PER/LOC, le modèle en dit PERSON/GPE/LOC
    entites = {"personnes": [], "organisations": [], "lieux": []}
    for ent in doc.ents:
        if parsing.est_bruit(ent.text):
            continue
        if ent.label_ in ("PER", "PERSON"):
            entites["personnes"].append(ent.text)
        elif ent.label_ == "ORG" or parsing.est_ecole(ent.text):
            entites["organisations"].append(ent.text)
        elif ent.label_ in ("LOC", "GPE"):
            entites["lieux"].append(ent.text)

    # regex S1 : plus fiables que le NER pour emails / téléphones / dates
    entites["emails"] = parsing.extraire_emails(texte)
    entites["telephones"] = parsing.extraire_telephones(texte)
    entites["dates"] = parsing.extraire_dates(texte)
    for cle in entites:
        entites[cle] = parsing.dedupe(entites[cle])
    return entites


def organisations(texte: str, langue: Optional[str] = "fr") -> list[str]:
    """Raccourci : seulement les organisations (pour réparer les expériences)."""
    return extraire_entites_avancees(texte, langue)["organisations"]
