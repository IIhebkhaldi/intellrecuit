# -*- coding: utf-8 -*-
"""
⭐ Livrable S4 — Démo de la version alpha du Module A (Stagiaire 1).

Parse les CVs de data/sample_cvs/ et montre le CVData COMPLET :
- A2 : NER multi-langue (le modèle suit la langue détectée)
- A3 : structuration (expériences, formations, langues, certifications)
- A4 : skills normalisés et catégorisés (ontologie + fuzzy matching)

    python demos/s4_module_demo.py
"""
import io
import json
import sys
import time
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")  # console Windows

from app.services import cv_intelligence
from app.services.cv_intelligence.skills_normalizer import normaliser_skill

DOSSIER_CVS = Path(__file__).parent.parent / "data" / "sample_cvs"


def ligne(titre: str):
    print("\n" + "=" * 70)
    print(f"  {titre}")
    print("=" * 70)


if __name__ == "__main__":
    fichiers = sorted(
        f for f in DOSSIER_CVS.iterdir()
        if f.suffix.lower() in (".pdf", ".docx", ".txt")
    )
    if not fichiers:
        print("Aucun CV — lance d'abord : python data/generer_cvs_test.py")
        sys.exit(1)

    ligne("DÉMO S4 — Module A version alpha : CVData complet")

    debut = time.perf_counter()
    resultats = [cv_intelligence.parser_cv(f.name, f.read_bytes()) for f in fichiers]
    duree = time.perf_counter() - debut
    print(f"\n{len(resultats)} CVs parsés en {duree:.2f} s")

    # ---- Vue d'ensemble : ce que la S4 ajoute par rapport à la S3 ----
    print(f"\n{'fichier':<26} | {'exp':>3} | {'edu':>3} | {'skills':>6} | {'langues':>7} | {'certifs':>7}")
    print("-" * 68)
    for cv in resultats:
        print(f"{cv.filename:<26} | {len(cv.experience):>3} | {len(cv.education):>3} "
              f"| {len(cv.skills):>6} | {len(cv.languages):>7} | {len(cv.certifications):>7}")

    # ---- A4 : la normalisation en action ----
    ligne("A4 — Normalisation des skills (exigence du cahier des charges)")
    for brut in ["Python 3", "python programming", "sklearn", "k8s", "postgress"]:
        resultat = normaliser_skill(brut)
        print(f"  {brut!r:<25} -> {resultat}")

    # ---- Top skills du lot (préfiguration du dashboard du Module C) ----
    compteur = Counter(s.name for cv in resultats for s in cv.skills)
    print("\nTop 5 des skills du lot :", compteur.most_common(5))

    # ---- Zoom : le CVData complet d'un CV (contrat du trinôme) ----
    ligne(f"JSON CVData complet — {resultats[0].filename}")
    print(json.dumps(resultats[0].model_dump(), indent=2, ensure_ascii=False))
