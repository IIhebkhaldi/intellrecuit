# -*- coding: utf-8 -*-
"""
Extraction des formations — cahier des charges §5.1 (A3).

Une formation = école + diplôme + spécialité + années.
Format d'entrée typique : "Diplôme, spécialité X — École (2019 - 2022)".
"""
import re
from typing import List

from app.schemas.shared import EducationItem

from .experience_parser import separer_titre_entreprise
from .section_detector import normaliser

_ANNEES = re.compile(r"\(?((?:19|20)\d{2})\s*(?:[-–—]|à|to)\s*((?:19|20)\d{2})\)?")
# lazy + lookahead : s'arrête AVANT " — École" pour ne pas avaler le nom d'école
_SPECIALITE = re.compile(
    r",?\s*sp[ée]cialit[ée]\s+(.+?)(?=\s+[-–—]\s+|\s+chez\s+|,|\(|$)",
    flags=re.IGNORECASE,
)

_MOTS_ECOLE = (
    "universite", "university", "ecole", "institut", "faculte", "iset",
    "esprit", "lycee", "polytechnique", "sorbonne", "insat", "enit", "college",
)


def _ressemble_ecole(texte: str) -> bool:
    t = normaliser(texte)
    return any(mot in t for mot in _MOTS_ECOLE)


def parser_formations(bloc: str) -> List[EducationItem]:
    """Un item = une ligne avec une plage d'années."""
    items: list[EducationItem] = []
    for ligne in bloc.split("\n"):
        ligne = ligne.strip()
        m = _ANNEES.search(ligne)
        if not m:
            continue
        debut, fin = int(m.group(1)), int(m.group(2))
        reste = (ligne[: m.start()] + ligne[m.end():]).strip(" \t-–—,.()")

        # spécialité éventuelle : "Ingénieur Informatique, spécialité Data & IA"
        field = None
        m_spec = _SPECIALITE.search(reste)
        if m_spec:
            field = m_spec.group(1).strip()
            reste = _SPECIALITE.sub("", reste).strip(" ,")

        # découpe diplôme / école
        gauche, droite = separer_titre_entreprise(reste)
        if droite:
            degree, school = gauche, droite
        elif "," in reste:  # "BSc Computer Science, University of Manchester"
            gauche, droite = reste.split(",", 1)
            if _ressemble_ecole(droite):
                degree, school = gauche.strip(), droite.strip()
            else:
                degree, school = reste, "?"
        else:
            degree, school = reste, "?"

        # sécurité : si on a inversé (école à gauche), on remet dans l'ordre
        if _ressemble_ecole(degree) and not _ressemble_ecole(school):
            degree, school = school, degree

        items.append(EducationItem(
            school=school or "?",
            degree=degree or None,
            field=field,
            start_year=debut,
            end_year=fin,
        ))
    return items
