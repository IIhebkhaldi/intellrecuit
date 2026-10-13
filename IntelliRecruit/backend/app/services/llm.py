# -*- coding: utf-8 -*-
"""
J8 — Service LLM (Groq API) : génération d'un résumé de profil candidat.

Règles de sécurité :
- La clé API vient de la variable d'environnement GROQ_API_KEY (fichier .env),
  JAMAIS en dur dans le code, JAMAIS commitée sur GitLab.
- Si la clé est absente ou la librairie non installée, on renvoie None avec
  un avertissement au lieu de faire planter le pipeline.
"""
import json
import os
from typing import Optional

MODELE_GROQ = "llama-3.3-70b-versatile"


def disponible() -> bool:
    try:
        import groq  # noqa: F401
    except ImportError:
        return False
    return bool(os.environ.get("GROQ_API_KEY"))


def generer_resume(texte_cv: str, entites: dict) -> Optional[str]:
    """Génère un résumé de 2-3 phrases du profil candidat via Groq.

    Prompt engineering appliqué (J8) :
    - rôle système clair
    - température basse (sortie stable)
    - contexte structuré (les entités extraites par le Module A)
    """
    if not disponible():
        return None

    from groq import Groq
    client = Groq(api_key=os.environ["GROQ_API_KEY"])

    prompt = (
        "Voici les informations extraites d'un CV par notre parseur :\n"
        f"{json.dumps(entites, ensure_ascii=False, indent=2)}\n\n"
        "Et un extrait du texte brut du CV :\n"
        f"{texte_cv[:1500]}\n\n"
        "Rédige un résumé professionnel du candidat en 2 à 3 phrases, en français."
    )

    reponse = client.chat.completions.create(
        model=MODELE_GROQ,
        messages=[
            {"role": "system",
             "content": "Tu es un assistant RH concis et factuel. "
                        "Tu ne mentionnes que des informations présentes dans le CV."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
        max_tokens=250,
    )
    return reponse.choices[0].message.content.strip()


def extraire_json_llm(texte_cv: str) -> Optional[dict]:
    """Bonus J8 : demande au LLM une extraction structurée en JSON strict.
    Montre la technique 'sortie JSON forcée' + parsing défensif (try/except)."""
    if not disponible():
        return None

    from groq import Groq
    client = Groq(api_key=os.environ["GROQ_API_KEY"])

    prompt = (
        "Extrais les informations de ce CV. Réponds UNIQUEMENT avec un JSON valide, "
        "sans texte autour, sans markdown, au format exact :\n"
        '{"nom": "...", "email": "...", "competences": ["..."], "annees_experience": 0}\n\n'
        f"CV :\n{texte_cv[:1500]}"
    )
    reponse = client.chat.completions.create(
        model=MODELE_GROQ,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=300,
    )
    brut = reponse.choices[0].message.content.strip()
    brut = brut.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(brut)
    except json.JSONDecodeError:
        return None  # le LLM peut se tromper : edge case géré, on ne plante pas
