# -*- coding: utf-8 -*-
"""
⭐ Livrable S6 — Mesure de la precision / recall du Module A.

Parse les CVs de data/sample_cvs/, compare à la vérité terrain annotée
(data/ground_truth.json) et affiche un rapport par champ + le score global
sur les champs clés de l'objectif O2 (nom, email, skills : cible ≥ 85%).

    python demos/s6_evaluation_demo.py
"""
import io
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")  # console Windows

from app.services import cv_intelligence
from app.services.cv_intelligence import evaluation

RACINE = Path(__file__).parent.parent
DOSSIER_CVS = RACINE / "data" / "sample_cvs"
GROUND_TRUTH = RACINE / "data" / "ground_truth.json"


def barre(p: float, largeur: int = 20) -> str:
    plein = round(p * largeur)
    return "█" * plein + "·" * (largeur - plein)


if __name__ == "__main__":
    ground_truth = json.loads(GROUND_TRUTH.read_text(encoding="utf-8"))

    # 1) Parser tous les CVs annotés
    predits = {}
    for f in sorted(DOSSIER_CVS.iterdir()):
        if f.name in ground_truth:
            predits[f.name] = cv_intelligence.parser_cv(f.name, f.read_bytes()).model_dump()

    nb = len(predits)
    print("=" * 72)
    print(f"  RAPPORT PRECISION / RECALL — Module A  ({nb} CVs annotés)")
    print("=" * 72)

    rapport = evaluation.evaluer_dataset(predits, ground_truth)

    # 2) Tableau par champ
    print(f"\n{'champ':<14} | {'precision':>9} | {'recall':>7} | {'F1':>5} | barre precision")
    print("-" * 72)
    for champ, m in rapport.items():
        print(f"{champ:<14} | {m['precision']:>9.0%} | {m['recall']:>7.0%} "
              f"| {m['f1']:>5.2f} | {barre(m['precision'])}")

    # 3) Score global sur l'objectif O2 (nom + email + skills)
    o2 = evaluation.score_global(rapport)  # first_name, last_name, email, skills
    print("\n" + "=" * 72)
    cible = "✅ ATTEINT" if o2["precision"] >= 0.85 else "⚠️ à améliorer"
    print(f"  OBJECTIF O2 (nom + email + skills) — cible precision ≥ 85%")
    print(f"  precision = {o2['precision']:.0%}   recall = {o2['recall']:.0%}   "
          f"F1 = {o2['f1']:.2f}   -> {cible}")
    print("=" * 72)

    # 4) Détail des erreurs les plus utiles à corriger (là où FP+FN est le plus grand)
    print("\nChamps à améliorer en priorité (le plus d'erreurs) :")
    tries = sorted(rapport.items(), key=lambda kv: kv[1]["fp"] + kv[1]["fn"], reverse=True)
    for champ, m in tries[:3]:
        if m["fp"] + m["fn"] == 0:
            continue
        print(f"  - {champ:<12} : {m['fp']} faux positifs, {m['fn']} valeurs ratées")

    cible_dataset = "✅ exigence cahier atteinte" if nb >= 100 else "à étendre vers 100+"
    print(f"\nNote : dataset de {nb} CVs annotés (généré par data/generer_cvs_test.py) "
          f"— cible cahier §5.1 : 100+ CVs annotés ({cible_dataset}).")
