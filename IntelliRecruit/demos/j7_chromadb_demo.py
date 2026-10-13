# -*- coding: utf-8 -*-
"""
J7 — Démo autonome : ChromaDB + recherche sémantique.

Lancer :  python demos/j7_chromadb_demo.py
(ne nécessite pas l'API — script d'apprentissage indépendant)
"""
import chromadb
from sentence_transformers import SentenceTransformer

print("Chargement du modèle d'embeddings (1re fois : téléchargement ~450 Mo)...")
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

client = chromadb.Client()
collection = client.create_collection("demo_cvs")

# 5 candidats fictifs (les mêmes que le J3 de la semaine 1)
cvs = {
    "cv_iheb":    "Étudiant BI à ESPRIT, Power BI, SQL, machine learning, Python, ETL",
    "cv_sarah":   "Développeuse Java backend, Spring Boot, microservices, 3 ans d'expérience",
    "cv_mohamed": "Data engineer, ETL Talend, SQL Server, data warehouse, Python",
    "cv_amen":    "Développeur frontend React, TypeScript, intégration d'API REST",
    "cv_nour":    "Analyste de données, SQL, dashboards, reporting, Excel avancé",
}

collection.add(
    ids=list(cvs.keys()),
    documents=list(cvs.values()),
    embeddings=model.encode(list(cvs.values())).tolist(),
)
print(f"{collection.count()} CVs indexés ✅\n")

offres = [
    "Stage Business Intelligence : dashboards Power BI et modélisation décisionnelle",
    "Développeur web frontend maîtrisant React",
]

for offre in offres:
    res = collection.query(
        query_embeddings=[model.encode(offre).tolist()], n_results=2
    )
    print(f"Offre : {offre}")
    for cv_id, dist in zip(res["ids"][0], res["distances"][0]):
        print(f"   -> {cv_id:12} (distance : {dist:.4f}  — plus petit = plus proche)")
    print()

print("Vérifie que le classement correspond à l'intuition ✅")
