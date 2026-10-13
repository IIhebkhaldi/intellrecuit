# -*- coding: utf-8 -*-
"""
Extraction de l'identité : nom, prénom, email, téléphone (+ localisation, LinkedIn).

Regex + heuristiques, en réutilisant les briques de base (services/parsing.py).
Convention J10 : champ introuvable = None.
"""
import re
from typing import Optional

from app.schemas.shared import IdentitySection
from app.services import parsing  # regex emails + heuristique nom

# ------------------------------------------------------------------
# Téléphone
# ------------------------------------------------------------------
# Indicatif international optionnel puis groupes de chiffres. Les faux
# positifs (années...) sont éliminés ensuite par _telephone_plausible.
_TEL_CANDIDAT = re.compile(
    r"(?<![\d\w])(?:\+\d{1,3}[\s\.\-]?)?\d{1,4}(?:[\s\.\-]?\d{1,4}){2,6}(?![\d\w])"
)


def _telephone_plausible(candidat: str) -> bool:
    chiffres = re.sub(r"\D", "", candidat)
    if not 8 <= len(chiffres) <= 14:
        return False
    # écarte "2021 2024" et autres paires d'années collées par l'extraction
    if re.fullmatch(r"(?:19|20)\d{2}\s*(?:19|20)\d{2}", candidat.strip()):
        return False
    return True


def extraire_telephone(texte: str) -> Optional[str]:
    for candidat in _TEL_CANDIDAT.findall(texte):
        if _telephone_plausible(candidat):
            return re.sub(r"\s+", " ", candidat.strip())
    return None


def extraire_email(texte: str) -> Optional[str]:
    emails = parsing.extraire_emails(texte)
    return emails[0] if emails else None


# ------------------------------------------------------------------
# Nom / prénom
# ------------------------------------------------------------------
_MOTS_A_IGNORER = {
    # méta-CV
    "curriculum", "vitae", "cv", "résumé", "resume", "profil", "profile",
    "contact", "à", "propos", "about", "me", "objectif", "objective",
    # titres de métier fréquents (mise en page CV design : le titre au-dessus du nom)
    "développeur", "developpeur", "developer", "ingénieur", "ingenieur",
    "engineer", "manager", "consultant", "analyst", "analyste",
    "designer", "architect", "architecte", "chef", "responsable",
    "senior", "junior", "confirmé", "confirme", "lead", "principal",
    "web", "software", "logiciel", "data", "backend", "frontend",
    "fullstack", "full", "stack", "mobile", "devops", "sre", "cloud",
    "professionnel", "professional", "freelance", "specialist", "spécialiste",
    "scientist", "scientifique", "coordinator", "coordinateur",
    "product", "project", "projet", "owner", "master", "scrum",
    "assistant", "directeur", "director", "student", "étudiant", "etudiant",
    "stagiaire", "intern", "trainee", "expert",
}


def _est_ligne_nom(ligne: str) -> bool:
    """Ligne qui ressemble à un nom : 2-4 mots alphabétiques, pas de bruit."""
    ligne = ligne.strip()
    if not (4 <= len(ligne) <= 60):
        return False
    mots = ligne.split()
    if not (2 <= len(mots) <= 4):
        return False
    if not all(re.fullmatch(r"[A-Za-zÀ-ÿ'\-]{2,}", m) for m in mots):
        return False
    if any(m.lower() in _MOTS_A_IGNORER for m in mots):
        return False
    if parsing.est_bruit(ligne):
        return False
    return True


def _decouper_nom(nom_complet: str) -> tuple[str, Optional[str]]:
    """Convention J10 : 1er mot = prénom, le reste = nom."""
    mots = nom_complet.strip().split()
    return mots[0], " ".join(mots[1:]) or None


def extraire_nom_prenom(texte: str) -> tuple[Optional[str], Optional[str]]:
    """Convention J10 : 1er mot = prénom, le reste = nom.

    Stratégie robuste pour les CVs design où le titre du poste
    ("Développeur Web Professionnel") apparaît AVANT le nom :

    - On scanne les 20 premières lignes non-vides
    - On retourne la 1ère qui ressemble à un nom (2-4 mots alphabétiques,
      pas dans _MOTS_A_IGNORER : ni "développeur", "ingénieur", "senior"...)
    - .title() pour normaliser "AMIRA BEN SALEM" -> "Amira Ben Salem"
    - Fallback : heuristique de base (5 premières lignes)
    """
    lignes = [l.strip() for l in texte.split("\n") if l.strip()][:20]

    for ligne in lignes:
        if _est_ligne_nom(ligne):
            return _decouper_nom(ligne.title())

    nom_complet = parsing.extraire_nom_candidat(texte)
    if nom_complet:
        return _decouper_nom(nom_complet)
    return None, None


# ------------------------------------------------------------------
# Bonus : LinkedIn + localisation
# ------------------------------------------------------------------
def extraire_linkedin(texte: str) -> Optional[str]:
    """Extrait l'URL du profil LinkedIn. Gère plusieurs formats réels.

    1) URL de profil complète : `[fr.]linkedin.com/in/<user>` (ou `/pub/`),
       avec ou sans `www` / `https` / sous-domaine régional, query ignorée.
    2) URL sans `/in/` : `linkedin.com/<user>` (hors pages non-profil).
    3) Libellé seul : « LinkedIn : prenom-nom » — on n'accepte qu'un handle
       contenant un tiret (slug type `prenom-nom`) pour ne pas confondre avec
       un prénom/nom isolé (préserve la précision).

    Les liens cliquables des PDF sont déjà réinjectés dans le texte par le
    parser (l'URL est souvent absente du texte visible).
    """
    # 1) profil : [xx.]linkedin.com/(in|pub)/<user>
    m = re.search(
        r"(?:[a-z]{2,3}\.)?linkedin\.com/(?:in|pub)/([A-Za-z0-9_%.\-]+)",
        texte, flags=re.IGNORECASE,
    )
    if m:
        return f"https://www.linkedin.com/in/{m.group(1).strip('.')}"

    # 2) linkedin.com/<user> sans '/in/' (hors pages non-profil)
    m = re.search(r"linkedin\.com/([A-Za-z0-9_%.\-]+)", texte, flags=re.IGNORECASE)
    if m and m.group(1).lower() not in {
        "in", "pub", "company", "school", "jobs", "feed", "groups",
    }:
        return f"https://www.linkedin.com/in/{m.group(1).strip('.')}"

    # 3) libellé « LinkedIn : prenom-nom » (handle avec au moins un tiret)
    m = re.search(
        r"linkedin\b[\s:@/·|•–—\-]*([a-z0-9]+(?:-[a-z0-9]+)+)",
        texte, flags=re.IGNORECASE,
    )
    if m:
        return f"https://www.linkedin.com/in/{m.group(1)}"

    return None


PAYS_CONNUS = (
    "tunisie|tunisia|france|maroc|morocco|algérie|algerie|algeria|"
    "canada|belgique|belgium|allemagne|germany|espagne|spain|italie|italy|"
    "royaume-uni|uk|usa|états-unis|etats-unis"
)
_LOC = re.compile(
    rf"([A-ZÀ-Ý][\wà-ÿ'\-]+(?:[ ][A-ZÀ-Ý]?[\wà-ÿ'\-]+)?)[ ]*,[ ]*({PAYS_CONNUS})\b",
    flags=re.IGNORECASE,
)


def extraire_localisation(texte: str) -> Optional[str]:
    """Cherche un motif 'Ville, Pays' dans l'en-tête du CV (15 premières lignes).

    On cherche ligne par ligne (et pas sur le bloc entier) pour que la ville
    ne "déborde" pas sur la ligne précédente à travers le saut de ligne.
    """
    for ligne in texte.split("\n")[:15]:
        m = _LOC.search(ligne)
        if m:
            ville, pays = m.group(1).strip(), m.group(2).strip()
            return f"{ville}, {pays.title()}"
    return None


def extraire_identite(texte: str) -> IdentitySection:
    texte = parsing.nettoyer_texte(texte)
    prenom, nom = extraire_nom_prenom(texte)
    return IdentitySection(
        first_name=prenom,
        last_name=nom,
        email=extraire_email(texte),
        phone=extraire_telephone(texte),
        location=extraire_localisation(texte),
        linkedin=extraire_linkedin(texte),
    )
