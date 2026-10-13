# -*- coding: utf-8 -*-
"""
Extraction des langues et des certifications — cahier des charges §5.1 (A3).

Langues : dictionnaire fermé (on ne garde que les vrais noms de langue, pour
ignorer le bruit d'extraction PDF) + normalisation des niveaux.
"""
import re
from typing import List

from app.schemas.shared import Language

from .section_detector import normaliser

# ------------------------------------------------------------------
# Langues : "Arabe (natif), Français (courant), Anglais (B2)"
# ------------------------------------------------------------------
_NOMS_LANGUES: dict[str, str] = {
    "arabe": "arabic", "arabic": "arabic",
    "francais": "french", "french": "french",
    "anglais": "english", "english": "english",
    "allemand": "german", "german": "german",
    "espagnol": "spanish", "spanish": "spanish",
    "italien": "italian", "italian": "italian",
    "chinois": "chinese", "chinese": "chinese",
    "japonais": "japanese", "japanese": "japanese",
    "turc": "turkish", "turkish": "turkish",
    "russe": "russian", "russian": "russian",
}
_NIVEAUX: dict[str, str] = {
    "natif": "native", "native": "native", "maternelle": "native",
    "courant": "fluent", "fluent": "fluent", "couramment": "fluent",
    "professionnel": "professional", "professional": "professional",
    "intermediaire": "intermediate", "intermediate": "intermediate",
    "debutant": "beginner", "beginner": "beginner", "notions": "beginner",
    "avance": "advanced", "advanced": "advanced", "bilingue": "native",
}
_LANGUE_ITEM = re.compile(r"([A-Za-zÀ-ÿ]+)\s*(?:\(([^)]+)\))?")


def parser_langues(bloc: str) -> List[Language]:
    """Ne garde que les mots qui sont VRAIMENT des langues (dict fermé) :
    le bloc peut contenir du bruit d'extraction PDF."""
    langues: list[Language] = []
    vus: set[str] = set()
    for m in _LANGUE_ITEM.finditer(bloc):
        nom = _NOMS_LANGUES.get(normaliser(m.group(1)))
        if not nom or nom in vus:
            continue
        vus.add(nom)
        niveau_brut = m.group(2)
        niveau = None
        if niveau_brut:
            niveau = _NIVEAUX.get(normaliser(niveau_brut), niveau_brut.strip())
        langues.append(Language(name=nom, level=niveau))
    return langues


# ------------------------------------------------------------------
# Certifications : une par ligne (ou séparées par des virgules)
# ------------------------------------------------------------------
def parser_certifications(bloc: str) -> List[str]:
    certifs: list[str] = []
    for item in re.split(r"[\n,;•]+", bloc):
        item = item.strip(" \t-–—·")
        if 3 <= len(item) <= 90:
            certifs.append(item)
    return certifs
