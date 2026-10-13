# -*- coding: utf-8 -*-
"""
Évaluation du Module A — precision / recall / F1 (Semaine 6).

Objectif du cahier des charges (O2) : ≥ 85% de precision sur nom, email, skills.
On compare la sortie du parser à une vérité terrain annotée (data/ground_truth.json)
et on calcule, par champ :
- precision = bonnes prédictions / prédictions faites
- recall    = bonnes prédictions / valeurs attendues
- F1        = moyenne harmonique des deux

Deux types de champs :
- simples (nom, email, téléphone...) : une valeur -> comparaison exacte normalisée
- listes (skills, langues)           : ensembles -> intersection / différences
"""
import re
from typing import Iterable, Optional


def _norm(v) -> Optional[str]:
    """Normalise pour une comparaison juste : minuscules, espaces réduits."""
    if v is None:
        return None
    s = re.sub(r"\s+", " ", str(v).strip().lower())
    return s or None


def _pr(tp: int, fp: int, fn: int) -> dict:
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    return {
        "precision": round(precision, 3),
        "recall": round(recall, 3),
        "f1": round(f1, 3),
        "tp": tp, "fp": fp, "fn": fn,
    }


def score_champ_simple(paires: Iterable[tuple]) -> dict:
    """paires = liste de (valeur_predite, valeur_attendue) pour UN champ simple.

    Règles (extraction mono-valeur) :
    - attendu présent et prédit == attendu   -> TP
    - attendu présent et prédit != attendu   -> FN (valeur ratée)
    - prédit présent et prédit != attendu    -> FP (valeur inventée/erronée)
    - attendu absent et prédit absent        -> rien (vrai négatif)
    """
    tp = fp = fn = 0
    for predit, attendu in paires:
        p, a = _norm(predit), _norm(attendu)
        if a is not None:
            if p == a:
                tp += 1
            else:
                fn += 1
                if p is not None:
                    fp += 1
        else:  # rien n'était attendu
            if p is not None:
                fp += 1
    return _pr(tp, fp, fn)


def score_champ_liste(paires: Iterable[tuple]) -> dict:
    """paires = liste de (liste_predite, liste_attendue) pour UN champ liste.

    Agrège les intersections/différences d'ensembles sur tous les CVs.
    """
    tp = fp = fn = 0
    for predit, attendu in paires:
        p = {_norm(x) for x in (predit or []) if _norm(x)}
        a = {_norm(x) for x in (attendu or []) if _norm(x)}
        tp += len(p & a)
        fp += len(p - a)
        fn += len(a - p)
    return _pr(tp, fp, fn)


# Champs simples de l'identité à évaluer + accès à la valeur prédite
CHAMPS_SIMPLES = {
    "first_name": lambda cv: cv["identity"]["first_name"],
    "last_name": lambda cv: cv["identity"]["last_name"],
    "email": lambda cv: cv["identity"]["email"],
    "phone": lambda cv: cv["identity"]["phone"],
    "location": lambda cv: cv["identity"]["location"],
    "linkedin": lambda cv: cv["identity"]["linkedin"],
    "language": lambda cv: cv.get("language"),
}


def evaluer_dataset(predits: dict, ground_truth: dict) -> dict:
    """Compare les CVData prédits à la vérité terrain.

    predits       : {filename -> CVData (dict)}
    ground_truth  : {filename -> valeurs attendues (dict)}  (clés '_...' ignorées)
    Retourne {champ -> {precision, recall, f1, tp, fp, fn}}.
    """
    fichiers = [f for f in ground_truth if not f.startswith("_") and f in predits]
    rapport = {}

    # champs simples
    for champ, get in CHAMPS_SIMPLES.items():
        paires = [(get(predits[f]), ground_truth[f].get(champ)) for f in fichiers]
        rapport[champ] = score_champ_simple(paires)

    # skills (liste d'objets {name,...})
    paires_skills = [
        ([s["name"] for s in predits[f]["skills"]], ground_truth[f].get("skills", []))
        for f in fichiers
    ]
    rapport["skills"] = score_champ_liste(paires_skills)

    # langues (liste d'objets {name,...})
    paires_langs = [
        ([l["name"] for l in predits[f]["languages"]], ground_truth[f].get("languages", []))
        for f in fichiers
    ]
    rapport["languages"] = score_champ_liste(paires_langs)

    return rapport


def score_global(rapport: dict, champs: Optional[list] = None) -> dict:
    """Micro-moyenne (somme des TP/FP/FN) sur un sous-ensemble de champs.

    Par défaut sur les champs clés de l'objectif O2 : nom, email, skills.
    """
    if champs is None:
        champs = ["first_name", "last_name", "email", "skills"]
    tp = sum(rapport[c]["tp"] for c in champs)
    fp = sum(rapport[c]["fp"] for c in champs)
    fn = sum(rapport[c]["fn"] for c in champs)
    return _pr(tp, fp, fn)
