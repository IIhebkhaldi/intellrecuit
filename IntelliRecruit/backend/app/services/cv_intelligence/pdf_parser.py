# -*- coding: utf-8 -*-
"""
Extraction du texte d'un PDF.

pypdf d'abord ; si l'extraction est « suspecte » (CVs design multi-colonnes),
on retente avec pdfplumber qui respecte mieux l'ordre visuel du texte.
Les deux outils sont prévus par le cahier des charges (§5.1, sous-module A1).
"""
import io
import re

from pypdf import PdfReader

_EMAIL_RE = re.compile(r"[\w\.\-]+@[\w\.\-]+\.\w{2,}")


def _extraction_suspecte(texte: str) -> bool:
    """Détecte les extractions pypdf 'jumbled' des CVs design (multi-colonnes).

    Signaux : peu de sauts de ligne pour un texte long (colonnes mélangées),
    ou aucune adresse email trouvée (extrêmement rare dans un vrai CV).
    """
    if len(texte.strip()) < 50:
        return True
    lignes = [l for l in texte.split("\n") if l.strip()]
    if not lignes:
        return True
    # 1 seule "ligne" pour 500+ caractères = texte à plat sans structure
    if len(texte) > 500 and len(lignes) < 5:
        return True
    if not _EMAIL_RE.search(texte):
        return True
    return False


def _extraire_hyperliens(reader: PdfReader) -> list[str]:
    """Récupère les URLs des liens cliquables (annotations PDF).

    Dans un vrai CV, « LinkedIn » / « GitHub » / « Portfolio » sont souvent des
    liens cliquables : l'URL n'apparaît PAS dans le texte visible, seulement
    dans l'annotation. Sans ça, l'extraction LinkedIn échoue sur ces CVs.
    """
    liens: list[str] = []
    for page in reader.pages:
        annots = page.get("/Annots")
        if not annots:
            continue
        try:
            annots = annots.get_object()
        except Exception:
            continue
        for annot in annots:
            try:
                action = annot.get_object().get("/A")
                if not action:
                    continue
                uri = action.get_object().get("/URI")
                if uri:
                    uri = str(uri)
                    if uri not in liens:
                        liens.append(uri)
            except Exception:
                continue
    return liens


def extraire_texte_pdf(contenu: bytes) -> str:
    """PDF (bytes) -> texte. Fallback pdfplumber si l'extraction pypdf est suspecte.

    Les URLs des hyperliens cliquables (souvent LinkedIn/GitHub, absents du
    texte visible) sont ajoutées à la fin pour que l'extraction puisse les voir.
    """
    try:
        reader = PdfReader(io.BytesIO(contenu))
        texte_pypdf = "\n".join(page.extract_text() or "" for page in reader.pages)
        liens = _extraire_hyperliens(reader)
    except Exception as e:
        raise ValueError(f"Impossible de lire le PDF : {e}")

    texte = texte_pypdf
    if _extraction_suspecte(texte_pypdf):
        # Fallback pdfplumber (bien meilleur sur les CVs design)
        try:
            import pdfplumber
            with pdfplumber.open(io.BytesIO(contenu)) as pdf:
                texte_plumber = "\n".join(p.extract_text() or "" for p in pdf.pages)
            # On garde celui qui a le plus d'infos utiles : email trouvé > pas d'email
            if _EMAIL_RE.search(texte_plumber) and not _EMAIL_RE.search(texte_pypdf):
                texte = texte_plumber
            elif len(texte_plumber.strip()) > len(texte_pypdf.strip()):
                texte = texte_plumber
        except Exception:
            pass

    # Ajout des URLs des liens cliquables (une par ligne) — sans doublon visible
    liens_utiles = [u for u in liens if u not in texte]
    if liens_utiles:
        texte = texte + "\n" + "\n".join(liens_utiles)
    return texte
