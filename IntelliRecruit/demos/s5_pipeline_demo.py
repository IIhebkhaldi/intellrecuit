# -*- coding: utf-8 -*-
"""
⭐ Livrable S5 (part Stagiaire 1) — Pipeline bout-en-bout : offre -> CVs -> match -> questions.

Démontre la chaîne complète A -> B -> C EN LOCAL, sans attendre les binômes :
- Module A (RÉEL) : mes vrais endpoints /api/jobs et /api/cv/parse (persistés en base)
- Module B (STUB) : matching mots-clés simple, à remplacer par le service de Mohamed
- Module C (STUB) : questions d'entretien template, à remplacer par le service d'Amen Allah

Les stubs respectent le contrat partagé (MatchResult, schemas/shared.py) : le jour
où B et C sont prêts, on remplace les 2 fonctions `_stub_*` par des appels HTTP,
sans rien changer au reste.

    python demos/s5_pipeline_demo.py
"""
import io
import os
import sys
import tempfile
from pathlib import Path

# Base de démo isolée (ne pollue pas la vraie DB) — AVANT d'importer l'app
os.environ["DATABASE_URL"] = f"sqlite:///{Path(tempfile.gettempdir()) / 'intellirecruit_demo.db'}"
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")  # console Windows

from fastapi.testclient import TestClient

from app.db.database import init_db
from app.main import app
from app.schemas.shared import MatchResult

DOSSIER_CVS = Path(__file__).parent.parent / "data" / "sample_cvs"


# ==================================================================
#  STUB Module B (Mohamed) — matching mots-clés simple
#  (= exactement le "premier score simple" prévu pour B en S3)
# ==================================================================
def _stub_matching(cv: dict, job: dict) -> MatchResult:
    cv_skills = {s["name"] for s in cv["skills"]}
    requis = set(job["required_skills"])
    bonus = set(job["bonus_skills"])

    matched = sorted(requis & cv_skills)
    missing = sorted(requis - cv_skills)
    bonus_matched = sorted(bonus & cv_skills)

    score_skills = len(matched) / len(requis) if requis else 0.0
    score = round(min(1.0, score_skills + 0.1 * len(bonus_matched)), 2)

    return MatchResult(
        cv_id=cv["id"],
        job_id=job["id"],
        global_score=score,
        scores_detail={"skills_match": round(score_skills, 2),
                       "bonus_match": len(bonus_matched)},
        explanation=f"{len(matched)}/{len(requis)} skills requis présents"
                    + (f" + {len(bonus_matched)} bonus" if bonus_matched else ""),
        matched_skills=matched,
        missing_skills=missing,
    )


# ==================================================================
#  STUB Module C (Amen Allah) — questions d'entretien template
# ==================================================================
def _stub_questions(cv: dict, job: dict) -> list[str]:
    prenom = cv["identity"].get("first_name") or "le candidat"
    top_skills = [s["name"] for s in cv["skills"][:3]]
    questions = [f"Pouvez-vous décrire votre expérience avec {sk} ?" for sk in top_skills]
    questions.append(f"Pourquoi postulez-vous au poste de {job['title']} ?")
    manque = sorted(set(job["required_skills"]) - {s["name"] for s in cv["skills"]})
    if manque:
        questions.append(f"Le poste demande {manque[0]} : comment l'aborderiez-vous ?")
    return questions


# ==================================================================
#  PIPELINE
# ==================================================================
def ligne(t):
    print("\n" + "=" * 68 + f"\n  {t}\n" + "=" * 68)


if __name__ == "__main__":
    init_db()
    client = TestClient(app)

    ligne("S5 — Pipeline bout-en-bout : offre -> CVs -> matching -> questions")

    # 1) Module A : créer une offre (endpoint RÉEL /api/jobs)
    offre = client.post("/api/jobs", json={
        "title": "Data Analyst Junior",
        "required_skills": ["python", "sql", "power bi"],
        "bonus_skills": ["machine learning"],
        "min_experience_years": 1,
        "location": "Tunis",
    }).json()
    print(f"\n[A] Offre créée : {offre['id']} — {offre['title']}")
    print(f"    skills requis : {offre['required_skills']}")

    # 2) Module A : parser tous les CVs (endpoint RÉEL /api/cv/parse, persistés)
    cvs = []
    for f in sorted(DOSSIER_CVS.iterdir()):
        if f.suffix.lower() not in (".pdf", ".docx", ".txt"):
            continue
        r = client.post("/api/cv/parse", files={"file": (f.name, f.read_bytes())})
        cvs.append(r.json())
    print(f"[A] {len(cvs)} CVs parsés et sauvegardés en base")

    # 3) Module B (STUB) : scorer chaque CV, puis classer
    classement = sorted(
        (_stub_matching(cv, offre) for cv in cvs),
        key=lambda m: m.global_score,
        reverse=True,
    )

    ligne("[B-stub] Classement des candidats pour l'offre")
    cv_par_id = {cv["id"]: cv for cv in cvs}
    for rang, m in enumerate(classement, 1):
        nom = cv_par_id[m.cv_id]["identity"].get("first_name") or m.cv_id
        print(f"  #{rang}  {nom:<10} score={m.global_score:<5} "
              f"| {m.explanation} | manque: {m.missing_skills or '—'}")

    # 4) Module C (STUB) : questions pour le meilleur candidat
    top = cv_par_id[classement[0].cv_id]
    ligne(f"[C-stub] Questions d'entretien — {top['identity'].get('first_name')}")
    for i, q in enumerate(_stub_questions(top, offre), 1):
        print(f"  {i}. {q}")

    print("\n✅ Pipeline complet fonctionnel. Les stubs B/C se remplacent par des")
    print("   appels HTTP aux services de Mohamed et Amen Allah, sans autre changement.")
