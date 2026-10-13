# -*- coding: utf-8 -*-
"""
Configuration de l'application (Annexe E : backend/app/config.py).

Charge le fichier .env situé à la RACINE du repo (là où est .env.example),
même quand uvicorn est lancé depuis backend/.
"""
import os
from pathlib import Path

# racine du repo : config.py -> app -> backend -> intellirecruit-semaine3
RACINE_REPO = Path(__file__).resolve().parents[2]

try:
    from dotenv import load_dotenv
    load_dotenv(RACINE_REPO / ".env")
except ImportError:
    pass  # python-dotenv optionnel : on peut aussi exporter la variable à la main


def groq_key_presente() -> bool:
    """Vrai si la clé Groq (pipeline S2) est disponible."""
    return bool(os.environ.get("GROQ_API_KEY"))
