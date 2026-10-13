# -*- coding: utf-8 -*-
"""
Détection des sections d'un CV et découpage en blocs — cahier des charges §5.1 (A3).

Reconnaît les en-têtes FR + EN (Expérience / Formation / Compétences / Langues /
Certifications / Projets) et découpe le texte en {section: contenu}.
"""
import re
import unicodedata
from typing import Optional

SECTIONS_CONNUES: dict[str, list[str]] = {
    "experience": [
        "experience professionnelle", "experiences professionnelles",
        "experience", "experiences", "work experience",
        "professional experience", "parcours professionnel", "emplois",
    ],
    "education": [
        "formation", "formations", "education", "etudes", "diplomes",
        "parcours academique", "academic background", "cursus",
        "formation academique", "formation professionnelle",
    ],
    "skills": [
        "competences", "competences cles", "competences techniques",
        "skills", "technical skills", "savoir-faire", "hard skills",
    ],
    "languages": ["langues", "languages"],
    "certifications": ["certifications", "certificats", "certificates"],
    "projects": ["projets", "projet", "projects", "projets academiques"],
}


def normaliser(texte: str) -> str:
    """Minuscules sans accents : 'COMPÉTENCES CLÉS' -> 'competences cles'.

    Helper partagé par les parsers d'expérience / formation / langues.
    """
    nfkd = unicodedata.normalize("NFKD", texte)
    sans_accents = "".join(c for c in nfkd if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", sans_accents.strip().lower())


def detecter_section(ligne: str) -> Optional[str]:
    """Retourne le nom canonique de la section si la ligne est un en-tête."""
    l = normaliser(ligne).strip(" :•-–—#")
    if not l or len(l) > 45:
        return None
    for nom, aliases in SECTIONS_CONNUES.items():
        if l in aliases:
            return nom
    # PDF extractors sometimes split words with spaces (e.g. "ÉDUCA TION")
    l_compact = l.replace(" ", "")
    if l_compact != l:
        for nom, aliases in SECTIONS_CONNUES.items():
            if l_compact in (a.replace(" ", "") for a in aliases):
                return nom
    return None


def decouper_sections(texte: str) -> dict[str, str]:
    """Découpe le texte du CV en blocs {section: contenu}.

    Tout ce qui précède la 1ère section connue va dans "entete"
    (c'est là que vit l'identité, traitée par identity_parser.py).
    """
    blocs: dict[str, list[str]] = {"entete": []}
    courante = "entete"
    for ligne in texte.split("\n"):
        section = detecter_section(ligne)
        if section:
            courante = section
            blocs.setdefault(courante, [])
        else:
            blocs.setdefault(courante, []).append(ligne)
    return {nom: "\n".join(lignes).strip() for nom, lignes in blocs.items()}
