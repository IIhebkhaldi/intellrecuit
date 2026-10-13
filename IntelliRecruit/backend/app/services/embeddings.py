# -*- coding: utf-8 -*-
"""
J7 — Service embeddings + recherche sémantique (ChromaDB).

Le modèle SentenceTransformer et ChromaDB sont chargés paresseusement :
si les librairies ne sont pas installées, l'API démarre quand même et
le pipeline renvoie un avertissement au lieu de planter (edge case géré).
"""
from typing import List, Optional

_st_model = None
_collection = None


def _charger():
    """Charge le modèle d'embeddings et la collection ChromaDB (1 seule fois)."""
    global _st_model, _collection
    if _st_model is None:
        from sentence_transformers import SentenceTransformer
        import chromadb
        _st_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
        client = chromadb.Client()  # en mémoire (PersistentClient(path=...) pour persister)
        _collection = client.get_or_create_collection("cvs")
    return _st_model, _collection


def disponible() -> bool:
    """Vrai si sentence-transformers + chromadb sont installés."""
    try:
        import sentence_transformers  # noqa: F401
        import chromadb  # noqa: F401
        return True
    except ImportError:
        return False


def indexer_cv(cv_id: str, texte: str, metadata: Optional[dict] = None) -> None:
    """Ajoute un CV dans la base vectorielle (embedding calculé automatiquement)."""
    model, collection = _charger()
    collection.upsert(
        ids=[cv_id],
        documents=[texte[:2000]],  # on limite la taille pour l'embedding
        embeddings=[model.encode(texte[:2000]).tolist()],
        metadatas=[metadata or {}],
    )


def chercher_similaires(texte: str, n: int = 3, exclure_id: Optional[str] = None) -> List[dict]:
    """Retourne les n CVs les plus proches sémantiquement du texte donné."""
    model, collection = _charger()
    if collection.count() == 0:
        return []
    res = collection.query(
        query_embeddings=[model.encode(texte[:2000]).tolist()],
        n_results=min(n + 1, collection.count()),
    )
    similaires = []
    for cv_id, distance in zip(res["ids"][0], res["distances"][0]):
        if cv_id == exclure_id:
            continue  # on ne se compare pas à soi-même
        similaires.append({"id": cv_id, "distance": round(float(distance), 4)})
    return similaires[:n]
