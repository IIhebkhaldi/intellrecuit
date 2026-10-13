# -*- coding: utf-8 -*-
"""Tests S6 — calcul des métriques precision / recall / F1."""
from app.services.cv_intelligence.evaluation import (
    evaluer_dataset,
    score_champ_liste,
    score_champ_simple,
    score_global,
)


# ---------- champ simple ----------
def test_simple_parfait():
    m = score_champ_simple([("a@x.tn", "a@x.tn"), ("b@x.tn", "b@x.tn")])
    assert m["precision"] == 1.0 and m["recall"] == 1.0 and m["f1"] == 1.0


def test_simple_normalisation():
    """La comparaison ignore casse et espaces superflus."""
    m = score_champ_simple([(" London,  UK ", "London, Uk")])
    assert m["precision"] == 1.0


def test_simple_faux_positif():
    """Prédire une valeur là où rien n'est attendu = faux positif."""
    m = score_champ_simple([("+216 22 000 000", None)])
    assert m["fp"] == 1 and m["tp"] == 0
    assert m["precision"] == 0.0


def test_simple_valeur_ratee():
    """Attendu présent mais rien prédit = valeur ratée (FN)."""
    m = score_champ_simple([(None, "Amira")])
    assert m["fn"] == 1 and m["tp"] == 0
    assert m["recall"] == 0.0


def test_simple_valeur_erronee_compte_fp_et_fn():
    """Une mauvaise valeur est à la fois FP (inventée) et FN (ratée)."""
    m = score_champ_simple([("Bob", "Amira")])
    assert m["fp"] == 1 and m["fn"] == 1 and m["tp"] == 0


def test_simple_vrai_negatif_ne_compte_pas():
    """Rien attendu, rien prédit -> aucun impact."""
    m = score_champ_simple([(None, None)])
    assert m == {"precision": 0.0, "recall": 0.0, "f1": 0.0, "tp": 0, "fp": 0, "fn": 0}


# ---------- champ liste ----------
def test_liste_intersection():
    # prédit {python, java}, attendu {python, sql} -> TP=1, FP=1 (java), FN=1 (sql)
    m = score_champ_liste([(["python", "java"], ["python", "sql"])])
    assert m["tp"] == 1 and m["fp"] == 1 and m["fn"] == 1
    assert m["precision"] == 0.5 and m["recall"] == 0.5


def test_liste_agrege_plusieurs_cvs():
    m = score_champ_liste([
        (["python"], ["python"]),
        (["sql", "aws"], ["sql"]),
    ])
    assert m["tp"] == 2 and m["fp"] == 1 and m["fn"] == 0


# ---------- dataset complet ----------
def test_evaluer_dataset_et_global():
    predits = {
        "cv1": {
            "language": "fr",
            "identity": {"first_name": "Amira", "last_name": "Ben Salem",
                         "email": "a@x.tn", "phone": None, "location": None,
                         "linkedin": None},
            "skills": [{"name": "python"}, {"name": "sql"}],
            "languages": [{"name": "french"}],
        }
    }
    gt = {
        "_desc": "ignore",
        "cv1": {
            "language": "fr", "first_name": "Amira", "last_name": "Ben Salem",
            "email": "a@x.tn", "phone": None, "location": None, "linkedin": None,
            "skills": ["python", "sql"], "languages": ["french"],
        },
    }
    rapport = evaluer_dataset(predits, gt)
    assert rapport["first_name"]["precision"] == 1.0
    assert rapport["email"]["recall"] == 1.0
    assert rapport["skills"]["f1"] == 1.0

    o2 = score_global(rapport)  # first_name, last_name, email, skills
    assert o2["precision"] == 1.0 and o2["recall"] == 1.0
