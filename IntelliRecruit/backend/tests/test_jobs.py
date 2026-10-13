# -*- coding: utf-8 -*-
"""Tests S5 — endpoints /api/jobs/* (CRUD des offres d'emploi)."""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

OFFRE = {
    "title": "Data Analyst Junior",
    "description": "Analyse de données, dashboards.",
    "required_skills": ["python", "sql"],
    "bonus_skills": ["power bi"],
    "min_experience_years": 1,
    "location": "Tunis",
    "remote_ok": True,
}


def test_creer_offre():
    r = client.post("/api/jobs", json=OFFRE)
    assert r.status_code == 201
    d = r.json()
    assert d["id"].startswith("job_")
    assert d["title"] == "Data Analyst Junior"
    assert d["required_skills"] == ["python", "sql"]
    assert d["remote_ok"] is True


def test_creer_offre_titre_obligatoire():
    """Le champ `title` est requis (validation Pydantic)."""
    r = client.post("/api/jobs", json={"description": "sans titre"})
    assert r.status_code == 422


def test_get_offre():
    jid = client.post("/api/jobs", json=OFFRE).json()["id"]
    r = client.get(f"/api/jobs/{jid}")
    assert r.status_code == 200
    assert r.json()["id"] == jid


def test_get_offre_inconnue():
    assert client.get("/api/jobs/job_inexistant").status_code == 404


def test_lister_offres():
    jid = client.post("/api/jobs", json=OFFRE).json()["id"]
    r = client.get("/api/jobs")
    assert r.status_code == 200
    assert any(o["id"] == jid for o in r.json())


def test_supprimer_offre():
    jid = client.post("/api/jobs", json=OFFRE).json()["id"]
    assert client.delete(f"/api/jobs/{jid}").status_code == 204
    assert client.get(f"/api/jobs/{jid}").status_code == 404


def test_supprimer_offre_inconnue():
    assert client.delete("/api/jobs/job_inexistant").status_code == 404


# --- S6 : endpoint métriques (utilisé par la page Streamlit) ---
def test_endpoint_metrics():
    r = client.get("/api/cv/metrics")
    assert r.status_code == 200
    data = r.json()
    assert data["nb_cvs"] >= 1
    assert "objectif_o2" in data and "par_champ" in data
    # l'objectif O2 (nom + email + skills) doit tenir la cible du cahier (≥ 85%)
    assert data["objectif_o2"]["precision"] >= 0.85
    # 'metrics' ne doit pas être capté par la route /{cv_id}
    assert "email" in data["par_champ"]
