# -*- coding: utf-8 -*-
"""
⭐ Livrable S3 — Démo de la brique de parsing basique (Module A, Stagiaire 1).

Parse tous les CVs de data/sample_cvs/ (PDF, DOCX, TXT) et affiche :
nom, email, téléphone (+ localisation, LinkedIn, langue détectée).

C'est LE script à lancer devant l'encadrant au point du vendredi :

    python demos/s3_parsing_demo.py

Il fonctionne sans API : il appelle directement services/cv_intelligence.py.
(La même brique est aussi exposée via POST /api/cv/parse — voir Swagger.)
"""
import io
import json
import sys
import time
from pathlib import Path

# Le code du Module A vit dans backend/ (structure Annexe E du cahier des charges)
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")  # console Windows

from app.services import cv_intelligence

DOSSIER_CVS = Path(__file__).parent.parent / "data" / "sample_cvs"


def afficher_tableau(resultats):
    colonnes = ["fichier", "format", "langue", "prénom", "nom", "email", "téléphone"]
    lignes = [
        [
            cv.filename,
            cv.format,
            cv.language or "?",
            cv.identity.first_name or "—",
            cv.identity.last_name or "—",
            cv.identity.email or "—",
            cv.identity.phone or "—",
        ]
        for cv in resultats
    ]
    largeurs = [max(len(str(l[i])) for l in [colonnes] + lignes) for i in range(len(colonnes))]
    sep = "-+-".join("-" * w for w in largeurs)
    print(" | ".join(c.ljust(w) for c, w in zip(colonnes, largeurs)))
    print(sep)
    for l in lignes:
        print(" | ".join(str(v).ljust(w) for v, w in zip(l, largeurs)))


if __name__ == "__main__":
    fichiers = sorted(
        f for f in DOSSIER_CVS.iterdir()
        if f.suffix.lower() in (".pdf", ".docx", ".txt")
    )
    if not fichiers:
        print(f"Aucun CV dans {DOSSIER_CVS} — lance d'abord : python data/generer_cvs_test.py")
        sys.exit(1)

    print("=" * 70)
    print("  DÉMO S3 — CV Intelligence Engine : parsing basique multi-format")
    print("=" * 70)

    debut = time.perf_counter()
    resultats = [cv_intelligence.parser_cv(f.name, f.read_bytes()) for f in fichiers]
    duree = time.perf_counter() - debut

    print(f"\n{len(resultats)} CVs parsés en {duree:.2f} s "
          f"({duree / len(resultats) * 1000:.0f} ms / CV)\n")
    afficher_tableau(resultats)

    # Zoom sur un CV : le JSON complet au format CVData (contrat du trinôme)
    print("\n" + "=" * 70)
    print(f"  JSON CVData complet — {resultats[0].filename}")
    print("=" * 70)
    print(json.dumps(resultats[0].model_dump(), indent=2, ensure_ascii=False))

    # Petit bilan des champs trouvés (préfiguration des métriques P/R de la S6)
    champs = ["first_name", "last_name", "email", "phone", "location", "linkedin"]
    print("\nChamps identité trouvés : ")
    for champ in champs:
        nb = sum(1 for cv in resultats if getattr(cv.identity, champ))
        print(f"  {champ:<12} {nb}/{len(resultats)}")
