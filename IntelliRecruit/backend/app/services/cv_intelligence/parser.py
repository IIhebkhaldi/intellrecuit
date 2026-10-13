# -*- coding: utf-8 -*-
"""
Extracteur de texte multi-format — point d'entrée de la couche A1.

Détecte le format d'après l'extension et dispatche vers le bon extracteur
(pdf_parser / docx_parser) ou lit directement le TXT.
"""
from .docx_parser import extraire_texte_docx
from .pdf_parser import extraire_texte_pdf

FORMATS_SUPPORTES = (".pdf", ".docx", ".txt")


def detecter_format(filename: str) -> str:
    """Retourne 'pdf' / 'docx' / 'txt', ou lève ValueError si non supporté."""
    nom = (filename or "").lower()
    for ext in FORMATS_SUPPORTES:
        if nom.endswith(ext):
            return ext[1:]
    raise ValueError(
        f"Format non supporté : {filename}. Formats acceptés : {FORMATS_SUPPORTES}"
    )


def extraire_texte_txt(contenu: bytes) -> str:
    """UTF-8 d'abord, sinon cp1252 (fichiers créés sous Windows)."""
    try:
        return contenu.decode("utf-8")
    except UnicodeDecodeError:
        return contenu.decode("cp1252", errors="replace")


def extraire_texte(filename: str, contenu: bytes) -> str:
    """Point d'entrée A1 : dispatch selon l'extension du fichier."""
    fmt = detecter_format(filename)
    if fmt == "pdf":
        return extraire_texte_pdf(contenu)
    if fmt == "docx":
        return extraire_texte_docx(contenu)
    return extraire_texte_txt(contenu)
