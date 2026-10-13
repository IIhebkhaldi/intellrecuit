# -*- coding: utf-8 -*-
"""
Extraction des expériences professionnelles — cahier des charges §5.1 (A3).

Une expérience = titre + entreprise + dates (start/end) + description + skills.
Contient aussi le parsing des plages de dates (réutilisé par education_parser),
au format "YYYY-MM" ; poste actuel -> end_date = None.
"""
import re
import unicodedata
from typing import List, Optional

from app.schemas.shared import ExperienceItem

from .section_detector import normaliser
from .skills_extractor import extraire_skills_texte

# ------------------------------------------------------------------
# Dates : "Juin 2025 - Août 2025", "2021 - 2024", "Janvier 2023 - présent",
#         "de Juin 2025 à Août 2025", "2022 - present"
# ------------------------------------------------------------------
MOIS_FR_EN: dict[str, int] = {
    "janvier": 1, "january": 1, "fevrier": 2, "february": 2, "mars": 3,
    "march": 3, "avril": 4, "april": 4, "mai": 5, "may": 5, "juin": 6,
    "june": 6, "juillet": 7, "july": 7, "aout": 8, "august": 8,
    "septembre": 9, "september": 9, "octobre": 10, "october": 10,
    "novembre": 11, "november": 11, "decembre": 12, "december": 12,
    # Abbreviated forms (accents already stripped by normaliser)
    "janv": 1, "fev": 2, "fevr": 2, "avr": 4, "juil": 7,
    "sept": 9, "oct": 10, "nov": 11, "dec": 12,
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9,
}
# Sort longest first so "septembre" matches before "sept"
_MOIS_PATTERN = "|".join(sorted(MOIS_FR_EN, key=len, reverse=True))

_ACTUEL = r"(?:pr[ée]sent|present|aujourd'hui|current|now|en cours|actuel)"

# NB : la regex s'applique au texte SANS accents ("à" devient "a", d'où \ba\b)
_PLAGE_DATES = re.compile(
    rf"(?:de\s+|from\s+)?"
    rf"((?:{_MOIS_PATTERN})\.?\s+)?((?:19|20)\d{{2}})"        # début : [mois[.]] année
    rf"\s*(?:[-–—]|\ba\b|\bto\b)\s*"                          # séparateur (- , à, to)
    rf"(?:((?:{_MOIS_PATTERN})\.?\s+)?((?:19|20)\d{{2}})|({_ACTUEL}))",  # fin ou 'présent'
    flags=re.IGNORECASE,
)

# "Juil. – Août 2025" : le mois de début n'a pas d'année, il hérite de celle de fin
_PLAGE_MOIS_ANNEE_PARTAGEE = re.compile(
    rf"(?:de\s+|from\s+)?"
    rf"({_MOIS_PATTERN})\.?\s*(?:[-–—]|\ba\b|\bto\b)\s*"
    rf"({_MOIS_PATTERN})\.?\s+((?:19|20)\d{{2}})",
    flags=re.IGNORECASE,
)


def _formater_date(mois: Optional[str], annee: str) -> str:
    """('juin', '2025') -> '2025-06' ; (None, '2021') -> '2021'."""
    if mois:
        cle = normaliser(mois).rstrip(".")
        numero = MOIS_FR_EN[cle]
        return f"{annee}-{numero:02d}"
    return annee


def _normaliser_accents_legers(ligne: str) -> str:
    """Enlève seulement les accents (garde la casse et la ponctuation) pour
    que la regex des mois marche sur 'Août' comme sur 'Aout'."""
    nfkd = unicodedata.normalize("NFKD", ligne)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def extraire_plage_dates(ligne: str) -> Optional[tuple[str, Optional[str], str]]:
    """Retourne (start_date, end_date, texte_sans_les_dates) ou None.

    end_date = None si le poste est actuel ('présent', 'current'...).
    """
    m = _PLAGE_DATES.search(_normaliser_accents_legers(ligne))
    if not m:
        return None
    debut = _formater_date(m.group(1), m.group(2))
    fin = None if m.group(5) else _formater_date(m.group(3), m.group(4))
    reste = (ligne[: m.start()] + " " + ligne[m.end():]).strip()
    return debut, fin, reste


# ------------------------------------------------------------------
# Séparation titre / entreprise (partagée avec education_parser)
# ------------------------------------------------------------------
_SEPARATEURS_TITRE_ENTREPRISE = [" — ", " – ", " - ", " chez ", " at ", " @ ", " | "]

_MOTS_DESCRIPTION = {
    "de", "des", "du", "la", "le", "les", "un", "une", "et", "en", "avec",
    "pour", "sur", "dans", "par", "aux", "au",
    "the", "of", "and", "for", "with", "in", "on", "to", "an", "a",
}


def _ressemble_description(texte: str) -> bool:
    """True if the text looks like a description rather than a company name."""
    mots = texte.lower().split()
    if len(mots) > 6:
        return True
    if len(mots) >= 3 and sum(1 for m in mots if m in _MOTS_DESCRIPTION) >= 2:
        return True
    return False


def separer_titre_entreprise(texte: str) -> tuple[str, str]:
    """'Stage Data Analyst chez Vermeg' -> ('Stage Data Analyst', 'Vermeg')."""
    texte = texte.strip(" \t-–—,.()")
    for sep in _SEPARATEURS_TITRE_ENTREPRISE:
        if sep in texte:
            titre, entreprise = texte.split(sep, 1)
            entreprise = entreprise.strip(" ,.-()")
            if _ressemble_description(entreprise):
                return texte, ""
            return titre.strip(" ,.-"), entreprise
    return texte, ""  # pas d'entreprise détectée


def parser_experiences(bloc: str) -> List[ExperienceItem]:
    """Un item démarre sur une ligne contenant une plage de dates ;
    les lignes suivantes (sans dates) sont sa description."""
    items: list[ExperienceItem] = []
    for ligne in bloc.split("\n"):
        ligne = ligne.strip()
        if not ligne:
            continue
        plage = extraire_plage_dates(ligne)
        if plage:
            debut, fin, reste = plage
            titre, entreprise = separer_titre_entreprise(reste)
            items.append(ExperienceItem(
                title=titre or "?",
                company=entreprise or "?",
                start_date=debut,
                end_date=fin,
            ))
        elif items:
            # ligne de description rattachée à la dernière expérience
            desc = items[-1].description
            items[-1].description = (desc + " " + ligne).strip()

    # skills mentionnés dans le titre + la description de chaque expérience
    for item in items:
        item.skills = extraire_skills_texte(f"{item.title} {item.description}")
    return items
