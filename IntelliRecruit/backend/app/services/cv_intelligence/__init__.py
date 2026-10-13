# -*- coding: utf-8 -*-
"""
CV Intelligence Engine — Module A (Stagiaire 1).

Transforme un fichier CV (PDF / DOCX / TXT) en JSON structuré `CVData`
(contrat J10, consommé par les Modules B et C).

Organisation du package (structure Annexe E du cahier des charges) :
- parser.py            : A1 — extracteur de texte multi-format (dispatch)
- pdf_parser.py        : A1 — extraction PDF (pypdf + fallback pdfplumber)
- docx_parser.py       : A1 — extraction DOCX (paragraphes + tableaux)
- language_detector.py : A1 — détection de langue fr/en/ar
- identity_parser.py   : identité (nom, email, téléphone, localisation, LinkedIn)
- ner.py               : A2 — NER spaCy multi-langue (filet de sécurité)
- section_detector.py  : A3 — détection + découpage des sections
- experience_parser.py : A3 — expériences + parsing des dates
- education_parser.py  : A3 — formations
- languages_parser.py  : A3 — langues + certifications
- skills_normalizer.py : A4 — ontologie + normalisation (fuzzy)
- skills_extractor.py  : A4 — extraction des skills
- cv_service.py        : orchestrateur -> CVData complet

L'historique (S2 structure/schemas, S3 identité, S4 NER/sections/skills) est
tracé dans les commits Git : un seul projet qui évolue, pas un dossier par semaine.
"""
# --- Orchestrateur (point d'entrée principal) ---
from .cv_service import parse_cv  # noqa: F401

# Alias de compatibilité (ancien nom utilisé par l'API et certains tests)
parser_cv = parse_cv

# --- A1 : extraction de texte + langue ---
from .parser import (  # noqa: F401
    FORMATS_SUPPORTES,
    detecter_format,
    extraire_texte,
    extraire_texte_txt,
)
from .pdf_parser import extraire_texte_pdf  # noqa: F401
from .docx_parser import extraire_texte_docx  # noqa: F401
from .language_detector import detecter_langue  # noqa: F401

# --- Identité ---
from .identity_parser import (  # noqa: F401
    extraire_email,
    extraire_identite,
    extraire_linkedin,
    extraire_localisation,
    extraire_nom_prenom,
    extraire_telephone,
)

# --- A3 : sections + items ---
from .section_detector import decouper_sections, detecter_section  # noqa: F401
from .experience_parser import extraire_plage_dates, parser_experiences  # noqa: F401
from .education_parser import parser_formations  # noqa: F401
from .languages_parser import parser_certifications, parser_langues  # noqa: F401

# --- A4 : skills ---
from .skills_normalizer import ONTOLOGIE, normaliser_skill  # noqa: F401
from .skills_extractor import (  # noqa: F401
    extraire_skills_cv,
    extraire_skills_texte,
    parser_section_skills,
)

# --- A2 : NER (sous-module accessible via cv_intelligence.ner) ---
from . import ner  # noqa: F401
