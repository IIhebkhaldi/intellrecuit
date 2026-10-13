# -*- coding: utf-8 -*-
"""
Modèles SQLAlchemy (Annexe E : backend/app/db/models.py).

Repris de l'Annexe A du cahier des charges (tables `cvs` et `jobs`). Le
CVData complet est stocké en JSON dans `parsed_data` (colonne JSONB en
PostgreSQL, TEXT/JSON en SQLite).
"""
from datetime import datetime, timezone

from sqlalchemy import JSON, Boolean, Column, DateTime, Integer, String, Text

from app.db.database import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


class CVRecord(Base):
    """Un CV parsé (sortie du Module A) stocké de façon persistante."""
    __tablename__ = "cvs"

    id = Column(String, primary_key=True)             # ex: "cv_1a2b3c4d"
    filename = Column(String(255))
    file_hash = Column(String(64), index=True)        # sha256 -> anti-doublons
    parsed_data = Column(JSON)                         # le CVData complet
    uploaded_at = Column(DateTime, default=_now)


class JobRecord(Base):
    """Une offre d'emploi (fonctionnalité F1 du cahier des charges)."""
    __tablename__ = "jobs"

    id = Column(String, primary_key=True)             # ex: "job_1a2b3c4d"
    title = Column(String(200), nullable=False)
    description = Column(Text, default="")
    required_skills = Column(JSON, default=list)
    bonus_skills = Column(JSON, default=list)
    min_experience_years = Column(Integer, default=0)
    location = Column(String(100))
    remote_ok = Column(Boolean, default=False)
    created_at = Column(DateTime, default=_now)
