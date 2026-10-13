# -*- coding: utf-8 -*-
"""
⭐ Mini-pipeline du trinôme (exercice de validation S2, conservé en S3).

POST /api/pipeline : parse CV -> embedding -> recherche similaire -> LLM résume.

Répartition :
- parse + entités        -> Iheb   (services/parsing.py + cv_intelligence.py)
- embedding + similaires -> Mohamed (services/embeddings.py)
- résumé LLM             -> Amen Allah (services/llm.py)

Mise à jour S3 : l'extraction de texte passe par cv_intelligence.extraire_texte,
donc le pipeline accepte maintenant aussi les DOCX et TXT.

Le pipeline est ROBUSTE : si ChromaDB / sentence-transformers ne sont pas
installés ou si la clé Groq est absente, il renvoie quand même les entités
avec des avertissements clairs (au lieu d'un crash 500).
"""
from fastapi import APIRouter, File, HTTPException, UploadFile

from app.schemas.shared import EntitiesResponse, PipelineResponse
from app.services import cv_intelligence, embeddings, llm, parsing

router = APIRouter(prefix="/api", tags=["Pipeline S2 (trinôme)"])


@router.post("/pipeline", response_model=PipelineResponse)
async def pipeline(file: UploadFile = File(...)):
    avertissements: list[str] = []

    # 1) Parsing + entités (Iheb — extraction multi-format S3 + logique NER S1)
    contenu = await file.read()
    try:
        cv_intelligence.detecter_format(file.filename)
        texte = cv_intelligence.extraire_texte(file.filename, contenu)
    except ValueError as e:
        code = 400 if "Format non supporté" in str(e) else 422
        raise HTTPException(status_code=code, detail=str(e))

    entites = EntitiesResponse(
        id=parsing.nouveau_cv_id(),
        filename=file.filename,
        nb_caracteres=len(texte),
        **parsing.extract_entities(texte),
    )

    # 2) Embedding + recherche de CVs similaires (Mohamed)
    similaires = []
    if embeddings.disponible():
        embeddings.indexer_cv(entites.id, texte, {"filename": file.filename})
        similaires = embeddings.chercher_similaires(texte, n=3, exclure_id=entites.id)
        if not similaires:
            avertissements.append(
                "Aucun autre CV dans la base vectorielle : uploade plusieurs CVs "
                "pour voir la recherche de similarité fonctionner."
            )
    else:
        avertissements.append(
            "sentence-transformers / chromadb non installés : "
            "étape 'similaires' ignorée (pip install -r requirements.txt)."
        )

    # 3) Résumé LLM (Amen Allah)
    resume = None
    if llm.disponible():
        resume = llm.generer_resume(texte, entites.model_dump())
    else:
        avertissements.append(
            "GROQ_API_KEY absente (ou librairie groq non installée) : "
            "étape 'resume' ignorée. Copie .env.example en .env et mets la clé."
        )

    return PipelineResponse(
        entites=entites,
        similaires=similaires,
        resume=resume,
        avertissements=avertissements,
    )
