# -*- coding: utf-8 -*-
"""Tests S5 — persistance des CVs en base + anti-doublon (file_hash)."""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

CV_TEXTE = (
    "AMIRA BEN SALEM\n"
    "Ariana, Tunisie\n"
    "amira.bensalem@gmail.com\n"
    "+216 22 345 678\n"
)


def _pdf(texte: str) -> bytes:
    from fpdf import FPDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", size=11)
    for ligne in texte.split("\n"):
        pdf.cell(0, 7, ligne, new_x="LMARGIN", new_y="NEXT")
    return bytes(pdf.output())


def test_cv_persiste_et_relisible():
    """Un CV parsé est sauvegardé puis relisible via GET (vient de la base)."""
    contenu = _pdf(CV_TEXTE)
    cid = client.post(
        "/api/cv/parse", files={"file": ("a.pdf", contenu, "application/pdf")}
    ).json()["id"]

    r = client.get(f"/api/cv/{cid}")
    assert r.status_code == 200
    assert r.json()["identity"]["email"] == "amira.bensalem@gmail.com"


def test_anti_doublon_meme_contenu():
    """Deux uploads du MÊME fichier -> un seul CV (dédup par hash)."""
    contenu = _pdf(CV_TEXTE)
    id1 = client.post(
        "/api/cv/parse", files={"file": ("a.pdf", contenu, "application/pdf")}
    ).json()["id"]
    id2 = client.post(
        "/api/cv/parse", files={"file": ("autre_nom.pdf", contenu, "application/pdf")}
    ).json()["id"]
    assert id1 == id2


def test_lister_cvs_contient_le_cv():
    contenu = _pdf(CV_TEXTE)
    cid = client.post(
        "/api/cv/parse", files={"file": ("a.pdf", contenu, "application/pdf")}
    ).json()["id"]
    r = client.get("/api/cv")
    assert r.status_code == 200
    assert any(c["id"] == cid for c in r.json())


# --- Suppression individuelle : verrouille qu'on ne vide PAS toute la table ---
def test_delete_supprime_uniquement_le_cv_cible():
    """Deux CVs en base, on en supprime UN : l'autre doit toujours être là."""
    cv1 = _pdf(CV_TEXTE + "cv-un\n")   # contenu différent -> hash différent
    cv2 = _pdf(CV_TEXTE + "cv-deux\n")
    id1 = client.post("/api/cv/parse",
                      files={"file": ("un.pdf", cv1, "application/pdf")}).json()["id"]
    id2 = client.post("/api/cv/parse",
                      files={"file": ("deux.pdf", cv2, "application/pdf")}).json()["id"]

    n_avant = len(client.get("/api/cv").json())
    assert client.delete(f"/api/cv/{id1}").status_code == 204

    restants = client.get("/api/cv").json()
    assert len(restants) == n_avant - 1                # UN SEUL supprimé
    assert any(c["id"] == id2 for c in restants)       # l'autre est intact
    assert client.get(f"/api/cv/{id1}").status_code == 404


def test_delete_cv_inconnu_donne_404():
    assert client.delete("/api/cv/cv_inexistant").status_code == 404
