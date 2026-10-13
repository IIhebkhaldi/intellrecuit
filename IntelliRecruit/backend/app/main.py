# -*- coding: utf-8 -*-
"""
IntelliRecruit — Backend FastAPI (Module A + endpoints communs).

Lancer (depuis le dossier backend/) :  uvicorn app.main:app --reload
Swagger : http://127.0.0.1:8000/docs
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import config
from app.api.cvs import router as cv_router
from app.api.jobs import router as jobs_router
from app.api.pipeline import router as pipeline_router
from app.db.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Au démarrage : crée les tables SQLite si besoin (S5)."""
    init_db()
    yield


app = FastAPI(
    title="IntelliRecruit — Backend (Module A)",
    description=(
        "CV Intelligence Engine : parsing PDF/DOCX/TXT, NER multi-langue, "
        "structuration et normalisation des skills -> CVData complet, persisté "
        "en base (S5). Endpoints /api/cv/*, /api/jobs/* (commun), /api/pipeline."
    ),
    version="0.5.0",
    lifespan=lifespan,
)

app.include_router(cv_router)
app.include_router(jobs_router)
app.include_router(pipeline_router)


@app.get("/health", tags=["Infra"])
def health():
    """Endpoint de vie : utile pour Docker healthcheck en S8."""
    return {
        "status": "ok",
        "groq_key_presente": config.groq_key_presente(),
    }
