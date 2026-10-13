# -*- coding: utf-8 -*-
"""
Orchestrateur du Module A : assemble toutes les briques en un CVData complet.

Pipeline :
  A1  extraction texte + langue      (parser + language_detector)
  ->  identité                       (identity_parser)
  A3  sections + items               (section_detector + *_parser)
  A4  skills normalisés              (skills_extractor)
  A2  NER en filet de sécurité       (ner)
"""
from app.schemas.shared import CVParseResponse
from app.services import parsing

from . import ner
from .education_parser import parser_formations
from .experience_parser import parser_experiences
from .identity_parser import extraire_identite
from .language_detector import detecter_langue
from .languages_parser import parser_certifications, parser_langues
from .parser import detecter_format, extraire_texte
from .section_detector import decouper_sections
from .skills_extractor import extraire_skills_cv


def parse_cv(filename: str, contenu: bytes) -> CVParseResponse:
    """Fichier brut (PDF/DOCX/TXT) -> CVData COMPLET (identité + sections)."""
    fmt = detecter_format(filename)
    texte = extraire_texte(filename, contenu)
    langue = detecter_langue(texte)

    # A3 — découpage en sections puis en items
    blocs = decouper_sections(texte)
    experience = parser_experiences(blocs.get("experience", ""))
    education = parser_formations(blocs.get("education", ""))
    langues = parser_langues(blocs.get("languages", ""))
    certifications = parser_certifications(blocs.get("certifications", ""))

    # A2 — filet de sécurité NER : entreprise manquante dans une expérience
    for item in experience:
        if item.company == "?":
            orgs = ner.organisations(f"{item.title} {item.description}", langue)
            if orgs:
                item.company = orgs[0]

    # A4 — skills : section Compétences (déclaratif) + skills cités dans les
    # descriptions d'expérience. On n'inclut PAS les intitulés de poste ni les
    # spécialités de formation (ce ne sont pas des compétences déclarées).
    liste_skills = extraire_skills_cv(
        blocs.get("skills", ""),
        descriptions_experience=[item.description for item in experience],
    )

    return CVParseResponse(
        id=parsing.nouveau_cv_id(),
        filename=filename,
        language=langue,
        identity=extraire_identite(texte),
        experience=experience,
        education=education,
        skills=liste_skills,
        languages=langues,
        certifications=certifications,
        format=fmt,
        nb_caracteres=len(texte),
    )
