# -*- coding: utf-8 -*-
"""
Router des endpoints /api/jobs/* — gestion des offres d'emploi (F1).

Endpoints communs aux 3 modules (Annexe E : api/jobs.py). Le matching du
Module B a besoin d'une offre pour scorer les CVs ; c'est ici qu'on la crée.

- POST   /api/jobs        : créer une offre -> JobData (id généré)
- GET    /api/jobs        : lister les offres
- GET    /api/jobs/{id}   : relire une offre
- DELETE /api/jobs/{id}   : supprimer une offre
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import crud
from app.db.database import get_session
from app.schemas.shared import JobCreate, JobData

router = APIRouter(prefix="/api/jobs", tags=["Offres d'emploi (commun)"])


@router.post("", response_model=JobData, status_code=201)
def creer_offre(data: JobCreate, db: Session = Depends(get_session)):
    """Crée une offre d'emploi (titre, skills requis, expérience min...)."""
    return crud.create_job(db, data)


@router.get("", response_model=list[JobData])
def lister_offres(db: Session = Depends(get_session)):
    return crud.list_jobs(db)


@router.get("/{job_id}", response_model=JobData)
def get_offre(job_id: str, db: Session = Depends(get_session)):
    job = crud.get_job(db, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"Offre {job_id} introuvable")
    return job


@router.delete("/{job_id}", status_code=204)
def supprimer_offre(job_id: str, db: Session = Depends(get_session)):
    if not crud.delete_job(db, job_id):
        raise HTTPException(status_code=404, detail=f"Offre {job_id} introuvable")
    return None
