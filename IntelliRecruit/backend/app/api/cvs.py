# -*- coding: utf-8 -*-
"""
Router des endpoints /api/cv/* (Module A).

Le CVData complet (identité + expériences + formations + skills + langues +
certifications) est désormais **persisté en base** (S5) : il survit au
redémarrage et devient référençable par son `id` depuis le Module B (matching).

Endpoints du cahier des charges :
- POST /api/cv/parse  : 1 fichier -> CVData complet (sauvegardé)
- POST /api/cv/batch  : plusieurs fichiers -> liste de CVData
- GET  /api/cv        : liste des CVs parsés (utile au matching / dashboard)
- GET  /api/cv/{id}   : relire un CV parsé
- POST /api/cv/debug  : texte brut extrait (diagnostic)
"""
import json

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app import config
from app.db import crud
from app.db.database import get_session
from app.schemas.shared import CVParseResponse
from app.services import cv_intelligence
from app.services.cv_intelligence import evaluation

router = APIRouter(prefix="/api/cv", tags=["Module A — CV"])


def _parser_fichier(db: Session, filename: str, contenu: bytes) -> CVParseResponse:
    """Validation format + anti-doublon (hash) + parsing + sauvegarde en base."""
    try:
        cv_intelligence.detecter_format(filename)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Anti-doublon (cahier : file_hash) : si ce fichier a déjà été parsé, on
    # renvoie le CV existant au lieu de le re-parser et de le dupliquer.
    file_hash = crud.hash_fichier(contenu)
    existant = crud.cv_par_hash(db, file_hash)
    if existant:
        return existant

    try:
        cv = cv_intelligence.parser_cv(filename, contenu)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    return crud.save_cv(db, cv, file_hash=file_hash)


@router.post("/parse", response_model=CVParseResponse)
async def parse_cv(file: UploadFile = File(...), db: Session = Depends(get_session)):
    """Parse un CV (PDF, DOCX ou TXT) et le sauvegarde -> CVData complet."""
    contenu = await file.read()
    return _parser_fichier(db, file.filename, contenu)


def _log_batch(nb: int):
    """Background task : s'exécute APRÈS la réponse HTTP."""
    print(f"[background] batch de {nb} CV(s) traité")


@router.post("/batch", response_model=list[CVParseResponse])
async def parse_batch(
    background_tasks: BackgroundTasks,
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_session),
):
    """Parse un lot de CVs (jusqu'à 500 dans la version finale)."""
    resultats = []
    for f in files:
        contenu = await f.read()
        resultats.append(_parser_fichier(db, f.filename, contenu))
    background_tasks.add_task(_log_batch, len(resultats))
    return resultats


@router.get("", response_model=list[CVParseResponse])
def lister_cvs(db: Session = Depends(get_session)):
    """Liste tous les CVs parsés (le Module B en a besoin pour le matching)."""
    return crud.list_cvs(db)


@router.get("/metrics", tags=["Module A — CV"])
def metrics():
    """Évalue le parser (precision/recall) sur le dataset annoté — livrable S6.

    Parse les CVs de data/sample_cvs/, compare à data/ground_truth.json et
    renvoie le rapport par champ + le score global sur l'objectif O2.
    (Défini AVANT /{cv_id} pour ne pas être capté par cette route.)
    """
    dossier_data = config.RACINE_REPO / "data"
    gt_path = dossier_data / "ground_truth.json"
    dossier_cvs = dossier_data / "sample_cvs"
    if not gt_path.exists() or not dossier_cvs.exists():
        raise HTTPException(status_code=404, detail="Dataset annoté introuvable (data/).")

    ground_truth = json.loads(gt_path.read_text(encoding="utf-8"))
    predits = {}
    for nom in ground_truth:
        if nom.startswith("_"):
            continue
        fichier = dossier_cvs / nom
        if fichier.exists():
            predits[nom] = cv_intelligence.parser_cv(nom, fichier.read_bytes()).model_dump()

    rapport = evaluation.evaluer_dataset(predits, ground_truth)
    return {
        "nb_cvs": len(predits),
        "objectif_o2": evaluation.score_global(rapport),  # nom + email + skills
        "par_champ": rapport,
    }


@router.get("/{cv_id}", response_model=CVParseResponse)
def get_cv(cv_id: str, db: Session = Depends(get_session)):
    """Retourne un CV déjà parsé (404 si inconnu)."""
    cv = crud.get_cv(db, cv_id)
    if cv is None:
        raise HTTPException(status_code=404, detail=f"CV {cv_id} introuvable")
    return cv


@router.delete("/{cv_id}", status_code=204)
def delete_cv(cv_id: str, db: Session = Depends(get_session)):
    """Supprime UN SEUL CV par son id (204 No Content si OK, 404 si inconnu).

    Passe par `crud.delete_cv` qui utilise l'accès par clé primaire :
    aucun risque de vider la table entière.
    """
    if not crud.delete_cv(db, cv_id):
        raise HTTPException(status_code=404, detail=f"CV {cv_id} introuvable")


@router.post("/debug")
async def debug_extraction(file: UploadFile = File(...)):
    """Utilitaire de debug : renvoie le texte brut extrait du fichier.

    Sert à comprendre POURQUOI un CV design donne des champs `null` : quand
    l'extraction est jumbled (colonnes mélangées), la ligne 'nom' n'est plus
    reconnaissable. On voit ici directement ce que pypdf/pdfplumber renvoient.
    """
    contenu = await file.read()
    try:
        cv_intelligence.detecter_format(file.filename)
        texte = cv_intelligence.extraire_texte(file.filename, contenu)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    lignes = texte.split("\n")
    return {
        "filename": file.filename,
        "nb_caracteres": len(texte),
        "nb_lignes": len(lignes),
        "20_premieres_lignes": lignes[:20],
        "texte_complet": texte,
    }
