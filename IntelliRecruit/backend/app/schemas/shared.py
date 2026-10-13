# -*- coding: utf-8 -*-
"""
J10 — Schema partagé CVData (contrat entre les Modules A, B et C).

C'est LA proposition à présenter à la réunion de validation du J10 avec
Mohamed, Amen Allah et l'encadrant. Basé sur l'Annexe B du cahier des charges.

Décisions à valider en réunion (noter les réponses ici en commentaire) :
- Format des dates : "YYYY-MM" (ex: "2025-06"). end_date = None -> poste actuel.
- Champ introuvable : None pour les champs simples, [] pour les listes.
- Langue du CV détectée : champ `language` ("fr" / "en" / "ar").
"""
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class IdentitySection(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin: Optional[str] = None


class ExperienceItem(BaseModel):
    title: str
    company: str
    start_date: Optional[str] = None  # "YYYY-MM"
    end_date: Optional[str] = None    # None = poste actuel
    description: str = ""
    skills: List[str] = Field(default_factory=list)


class EducationItem(BaseModel):
    school: str
    degree: Optional[str] = None
    field: Optional[str] = None
    start_year: Optional[int] = None
    end_year: Optional[int] = None


class Skill(BaseModel):
    name: str                      # normalisé, ex: "python"
    category: str = "unknown"      # language / framework / cloud / database / methodology
    level: Optional[str] = None    # beginner / intermediate / advanced


class Language(BaseModel):
    name: str                      # ex: "french"
    level: Optional[str] = None    # ex: "native", "B2", "professional"


class CVData(BaseModel):
    """Sortie du Module A, consommée par les Modules B et C."""
    id: str
    filename: Optional[str] = None
    language: Optional[str] = None  # langue détectée du CV : fr / en / ar
    identity: IdentitySection = Field(default_factory=IdentitySection)
    experience: List[ExperienceItem] = Field(default_factory=list)
    education: List[EducationItem] = Field(default_factory=list)
    skills: List[Skill] = Field(default_factory=list)
    languages: List[Language] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)


# ------------------------------------------------------------------
# Offres d'emploi (contrat commun J10 — utilisé par les 3 modules)
# Basé sur la table `jobs` de l'Annexe A du cahier des charges.
# ------------------------------------------------------------------
class JobData(BaseModel):
    """Une offre d'emploi. Consommée par tous les modules (matching, dashboard)."""
    id: str
    title: str
    description: str = ""
    required_skills: List[str] = Field(default_factory=list)
    bonus_skills: List[str] = Field(default_factory=list)
    min_experience_years: int = 0
    location: Optional[str] = None
    remote_ok: bool = False


class JobCreate(BaseModel):
    """Corps de POST /api/jobs (l'`id` est généré par le serveur)."""
    title: str
    description: str = ""
    required_skills: List[str] = Field(default_factory=list)
    bonus_skills: List[str] = Field(default_factory=list)
    min_experience_years: int = 0
    location: Optional[str] = None
    remote_ok: bool = False


class MatchResult(BaseModel):
    """Sortie du Module B (matching), consommée par le Module C (dashboard).

    Défini ici dans le contrat commun ; l'implémentation est celle de Mohamed.
    """
    cv_id: str
    job_id: str
    global_score: float
    scores_detail: Dict[str, float] = Field(default_factory=dict)
    explanation: str = ""
    matched_skills: List[str] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)


# --- Schemas de réponse API ---

class CVParseResponse(CVData):
    """Réponse S3 de /api/cv/parse et /api/cv/batch.

    Hérite du contrat CVData (inchangé pour Mohamed et Amen Allah) et ajoute
    des infos techniques utiles pour la démo et le debug du Module A.
    """
    format: str = "pdf"        # pdf / docx / txt
    nb_caracteres: int = 0



class EntitiesResponse(BaseModel):
    """Entités extraites (logique S1) — encore utilisée par /api/pipeline (S2)."""
    id: str
    filename: str
    nb_caracteres: int
    personnes: List[str] = Field(default_factory=list)
    organisations: List[str] = Field(default_factory=list)
    lieux: List[str] = Field(default_factory=list)
    dates: List[str] = Field(default_factory=list)
    emails: List[str] = Field(default_factory=list)
    telephones: List[str] = Field(default_factory=list)


class PipelineResponse(BaseModel):
    """Réponse de /api/pipeline (exercice de validation S2)."""
    entites: EntitiesResponse
    similaires: List[dict] = Field(default_factory=list)
    resume: Optional[str] = None
    avertissements: List[str] = Field(default_factory=list)
