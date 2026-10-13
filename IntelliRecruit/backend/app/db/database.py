# -*- coding: utf-8 -*-
"""
Connexion à la base de données (Annexe E : backend/app/db/).

SQLAlchemy 2.x (ORM imposé par le cahier des charges §7). En dev on utilise
SQLite (fichier local) ; le passage à PostgreSQL en prod se fera en changeant
la seule variable DATABASE_URL, sans toucher au reste du code.
"""
import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Racine du repo : db -> app -> backend -> IntelliRecruit
RACINE_REPO = Path(__file__).resolve().parents[3]
_DB_PAR_DEFAUT = f"sqlite:///{RACINE_REPO / 'intellirecruit.db'}"

# Surchargeable par variable d'environnement (les tests pointent vers une DB isolée)
DATABASE_URL = os.environ.get("DATABASE_URL", _DB_PAR_DEFAUT)

# check_same_thread=False : nécessaire pour SQLite avec FastAPI (multi-thread)
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def init_db() -> None:
    """Crée les tables si elles n'existent pas encore (appelé au démarrage)."""
    from app.db import models  # noqa: F401  (enregistre les tables sur Base)
    Base.metadata.create_all(bind=engine)


def get_session():
    """Dépendance FastAPI : ouvre une session par requête et la referme après."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
