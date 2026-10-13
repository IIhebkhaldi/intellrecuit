# -*- coding: utf-8 -*-
"""
Opérations base de données (CRUD) pour les CVs et les offres.

Sépare l'accès aux données de la logique HTTP (routers) : les endpoints
appellent ces fonctions, testables indépendamment.
"""
import hashlib
import uuid
from typing import List, Optional

from sqlalchemy.orm import Session

from app.db.models import CVRecord, JobRecord
from app.schemas.shared import CVParseResponse, JobCreate, JobData


# ------------------------------------------------------------------
# CVs
# ------------------------------------------------------------------
def hash_fichier(contenu: bytes) -> str:
    """sha256 du fichier — sert à détecter les doublons (cahier : file_hash)."""
    return hashlib.sha256(contenu).hexdigest()


def cv_par_hash(db: Session, file_hash: str) -> Optional[CVParseResponse]:
    """Retrouve un CV déjà parsé à partir du hash de son fichier (anti-doublon)."""
    rec = db.query(CVRecord).filter(CVRecord.file_hash == file_hash).first()
    return CVParseResponse(**rec.parsed_data) if rec else None


def save_cv(db: Session, cv: CVParseResponse, file_hash: Optional[str] = None) -> CVParseResponse:
    """Insère (ou remplace) un CV parsé. Retourne le CVData tel quel."""
    rec = CVRecord(
        id=cv.id,
        filename=cv.filename,
        file_hash=file_hash,
        parsed_data=cv.model_dump(),
    )
    db.merge(rec)  # merge = upsert (insert ou update sur la clé primaire)
    db.commit()
    return cv


def get_cv(db: Session, cv_id: str) -> Optional[CVParseResponse]:
    rec = db.get(CVRecord, cv_id)
    return CVParseResponse(**rec.parsed_data) if rec else None


def list_cvs(db: Session) -> List[CVParseResponse]:
    return [CVParseResponse(**r.parsed_data) for r in db.query(CVRecord).all()]


def count_cvs(db: Session) -> int:
    return db.query(CVRecord).count()


def delete_cv(db: Session, cv_id: str) -> bool:
    """Supprime UN SEUL CV par son id. Retourne False si l'id n'existe pas.

    Utilise `db.get(CVRecord, cv_id)` (accès par clé primaire) puis `db.delete`
    sur cette instance : garantit qu'on ne touche QUE ce CV — jamais toute la
    table (bug à éviter : un `db.query(CVRecord).delete()` sans filtre viderait
    tout).
    """
    rec = db.get(CVRecord, cv_id)
    if not rec:
        return False
    db.delete(rec)
    db.commit()
    return True


# ------------------------------------------------------------------
# Offres d'emploi
# ------------------------------------------------------------------
def _to_jobdata(rec: JobRecord) -> JobData:
    return JobData(
        id=rec.id,
        title=rec.title,
        description=rec.description or "",
        required_skills=rec.required_skills or [],
        bonus_skills=rec.bonus_skills or [],
        min_experience_years=rec.min_experience_years or 0,
        location=rec.location,
        remote_ok=bool(rec.remote_ok),
    )


def create_job(db: Session, data: JobCreate) -> JobData:
    rec = JobRecord(id=f"job_{uuid.uuid4().hex[:8]}", **data.model_dump())
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return _to_jobdata(rec)


def get_job(db: Session, job_id: str) -> Optional[JobData]:
    rec = db.get(JobRecord, job_id)
    return _to_jobdata(rec) if rec else None


def list_jobs(db: Session) -> List[JobData]:
    return [_to_jobdata(r) for r in db.query(JobRecord).all()]


def delete_job(db: Session, job_id: str) -> bool:
    rec = db.get(JobRecord, job_id)
    if not rec:
        return False
    db.delete(rec)
    db.commit()
    return True
