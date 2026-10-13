# -*- coding: utf-8 -*-
"""
Extraction des compétences depuis le CV — cahier des charges §5.1 (A4).

Deux sources : la section Compétences (fiable, contexte clair) et le scan du
texte complet (pour les skills cités dans les expériences). S'appuie sur
l'ontologie et la normalisation de skills_normalizer.
"""
import re
from typing import List

from app.schemas.shared import Skill

from .skills_normalizer import (
    ALIAS_AMBIGUS,
    ALIAS_VERS_SKILL,
    ONTOLOGIE,
    normaliser_skill,
)


def _pattern_alias(alias: str) -> re.Pattern:
    """Regex avec 'frontières de mot' qui marche aussi pour c++ / c# / .net."""
    return re.compile(
        r"(?<![\w+#.])" + re.escape(alias) + r"(?![\w+#])",
        flags=re.IGNORECASE,
    )


# Patterns compilés une seule fois pour le scan du texte libre
_PATTERNS_TEXTE_LIBRE: list[tuple[re.Pattern, str]] = [
    (_pattern_alias(alias), canonique)
    for alias, canonique in ALIAS_VERS_SKILL.items()
    if alias not in ALIAS_AMBIGUS
]


def extraire_skills_texte(texte: str) -> List[str]:
    """Scanne un texte libre et retourne les skills canoniques trouvés.

    Les frontières de mot évitent déjà 'javascript' -> 'java'. En plus, on
    déduplique les **alias chevauchants** par position : si le span d'un skill
    est entièrement contenu dans celui d'un autre, on écarte le plus court.
    Exemple : dans « SQL Server », on garde 'sql server' et on écarte 'sql'
    (gain de précision — retour encadrant S7).
    """
    # 1) tous les matches avec leur position (start, end, canonique)
    matches: list[tuple[int, int, str]] = []
    for pattern, canonique in _PATTERNS_TEXTE_LIBRE:
        for m in pattern.finditer(texte):
            matches.append((m.start(), m.end(), canonique))

    # 2) traiter les spans les plus longs d'abord, écarter ceux qui sont inclus
    matches.sort(key=lambda x: x[1] - x[0], reverse=True)
    gardes: list[tuple[int, int, str]] = []
    trouves: list[str] = []
    for start, end, canonique in matches:
        inclus = any(
            gs <= start and end <= ge and gc != canonique
            for gs, ge, gc in gardes
        )
        if inclus:
            continue
        gardes.append((start, end, canonique))
        if canonique not in trouves:
            trouves.append(canonique)

    # 3) ordre stable : par première apparition dans le texte
    return sorted(trouves, key=lambda c: min(s for s, _, k in gardes if k == c))


def parser_section_skills(bloc: str) -> List[Skill]:
    """Parse la section Compétences d'un CV (items séparés par , ; • ou lignes).

    Chaque item passe par normaliser_skill : les alias ambigus ('C', 'R'...)
    sont acceptés ici car la section Compétences lève l'ambiguïté.
    """
    skills: list[Skill] = []
    vus: set[str] = set()
    for item in re.split(r"[,;•|\n•]+", bloc):
        item = item.strip(" \t-–—·")
        if not item or len(item) > 40:
            continue
        resultat = normaliser_skill(item)
        if resultat and resultat[0] not in vus:
            vus.add(resultat[0])
            skills.append(Skill(name=resultat[0], category=resultat[1]))
    return skills


def extraire_skills_cv(
    bloc_section: str = "",
    descriptions_experience: List[str] | None = None,
) -> List[Skill]:
    """Deux sources FIABLES : la section Compétences + les skills réellement
    cités dans les **descriptions** d'expérience.

    On ne scanne volontairement PAS le document entier. Un skill présent
    seulement dans un intitulé de poste (« Ingénieur Machine Learning »), une
    spécialité de formation (« spécialité Business Intelligence ») ou l'en-tête
    n'est PAS une compétence déclarée par le candidat : le scanner créait des
    faux positifs (retour encadrant). En se limitant à la section Compétences
    (déclaratif) et aux descriptions d'expérience (usage concret : « développé
    en React et Node.js »), on gagne en précision sans perdre de recall.

    Le `level` reste None : impossible de le déduire de façon fiable sans
    annotation — décision documentée (convention J10 : inconnu = None).
    """
    skills = parser_section_skills(bloc_section)
    vus = {s.name for s in skills}

    texte_descriptions = " ".join(d for d in (descriptions_experience or []) if d)
    for canonique in extraire_skills_texte(texte_descriptions):
        if canonique not in vus:
            vus.add(canonique)
            skills.append(Skill(name=canonique, category=ONTOLOGIE[canonique][0]))
    return skills
