# -*- coding: utf-8 -*-
"""
Détection de la langue du CV (fr / en / ar) — cahier des charges §5.1 (A1).

Un CV est surtout une liste de technologies (souvent en anglais), ce qui
trompe facilement langdetect. On vote donc sur des mots-outils quasi
exclusifs à chaque langue, avec langdetect en dernier recours.
"""
import re
from typing import Optional

# Mots-outils très fréquents et quasi exclusifs à chaque langue.
_MOTS_FR = re.compile(
    r"\b(de|des|du|la|le|les|et|à|chez|avec|pour|sur|dans|une|un|au|aux|été)\b",
    flags=re.IGNORECASE,
)
_MOTS_EN = re.compile(
    r"\b(the|and|of|at|in|with|for|to|on|from|by|built|using)\b",
    flags=re.IGNORECASE,
)
_CARACTERES_ARABES = re.compile(r"[؀-ۿ]")
_ACCENTS_FR = re.compile(r"[éèêëàâçùûôîï]", flags=re.IGNORECASE)


def detecter_langue(texte: str) -> Optional[str]:
    """Détection de langue adaptée aux CVs. None si indécidable.

    1. Caractères arabes -> 'ar'
    2. Vote de mots-outils : "de/et/chez..." vs "the/of/with..."
       (+ les accents français comptent : un CV anglais n'en a presque jamais)
    3. Égalité ou aucun indice -> langdetect en secours (fr/en/ar privilégiés)
    """
    extrait = texte.strip()[:2000]
    if len(extrait) < 20:
        return None

    if len(_CARACTERES_ARABES.findall(extrait)) > 20:
        return "ar"

    score_fr = len(_MOTS_FR.findall(extrait)) + min(len(_ACCENTS_FR.findall(extrait)), 5)
    score_en = len(_MOTS_EN.findall(extrait))
    if score_fr > score_en:
        return "fr"
    if score_en > score_fr:
        return "en"

    # Aucun indice décisif : langdetect en dernier recours
    try:
        from langdetect import DetectorFactory, detect_langs
        DetectorFactory.seed = 42  # résultats reproductibles (langdetect est stochastique)
        candidates = detect_langs(extrait)
        for lang in candidates:  # déjà triées par probabilité décroissante
            if lang.lang in ("fr", "en", "ar"):
                return lang.lang
        return candidates[0].lang if candidates else None
    except Exception:
        return None
