# -*- coding: utf-8 -*-
"""
Configuration pytest : base de données ISOLÉE pour les tests.

DATABASE_URL est défini AVANT tout import de l'app, pour que les tests
n'écrivent jamais dans la vraie base de dev (intellirecruit.db).
"""
import os
import pathlib
import tempfile

# DB de test dédiée (repartie propre à chaque session) — doit précéder les imports app
_TEST_DB = pathlib.Path(tempfile.gettempdir()) / "intellirecruit_test.db"
if _TEST_DB.exists():
    _TEST_DB.unlink()
os.environ["DATABASE_URL"] = f"sqlite:///{_TEST_DB}"

import pytest

from app.db import models  # noqa: F401  (enregistre les tables sur Base)
from app.db.database import Base, engine, init_db


@pytest.fixture(scope="session", autouse=True)
def _preparer_base():
    """Crée les tables avant les tests, les supprime après."""
    Base.metadata.drop_all(bind=engine)
    init_db()
    yield
    Base.metadata.drop_all(bind=engine)
