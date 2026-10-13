# -*- coding: utf-8 -*-
"""Tests unitaires du service de parsing (logique S1 réutilisée)."""
import pytest

from app.services.parsing import (
    dedupe,
    est_bruit,
    est_ecole,
    extraire_dates,
    extraire_emails,
    extraire_nom_candidat,
    extraire_telephones,
    nettoyer_texte,
)


# ---------- nettoyage ----------
def test_nettoyage_icones_email():
    """Le bruit des polices d'icônes ne doit plus coller à l'email."""
    sale = "/envel⌢pekiheb001@gmail.com"
    assert extraire_emails(nettoyer_texte(sale)) == ["kiheb001@gmail.com"]


def test_nettoyage_espaces():
    assert nettoyer_texte("a    b\t\tc") == "a b c"


# ---------- filtres ----------
def test_est_bruit_section():
    assert est_bruit("RÉSUMÉ") is True
    assert est_bruit("RÉSUMÉ Étudiant") is True  # entité qui commence par une section


def test_est_bruit_competence():
    assert est_bruit("Régression") is True
    assert est_bruit("Keras") is True
    assert est_bruit("Power BI") is True


def test_est_bruit_vrai_lieu_et_org():
    assert est_bruit("Tunis") is False
    assert est_bruit("Tunisie Télécom") is False


def test_est_bruit_fragment_elision():
    assert est_bruit("École d’") is True


def test_est_ecole():
    assert est_ecole("Lycée Abou Kacem") is True
    assert est_ecole("Tunisie Télécom") is False


# ---------- regex ----------
def test_extraire_emails():
    assert extraire_emails("a@b.tn et x.y-z@mail.co.uk") == ["a@b.tn", "x.y-z@mail.co.uk"]


def test_extraire_telephones_groupe_non_capturant():
    """Bug S1 corrigé : findall doit renvoyer les numéros COMPLETS."""
    tels = extraire_telephones("Appelez le +216 21 094 951 ou le 55 123 456.")
    assert "+216 21 094 951" in tels
    assert "55 123 456" in tels


def test_extraire_dates_plages_sans_doublons():
    dates = extraire_dates("Stage Juillet 2025 – Août 2025 puis projet 2021 – 2024.")
    assert "Juillet 2025 – Août 2025" in dates
    assert "2021 – 2024" in dates
    # les composantes de la plage ne doivent PAS ressortir en double
    assert "Juillet 2025" not in dates
    assert "2021" not in dates


def test_extraire_dates_simples():
    assert "Mai 2024" in extraire_dates("Diplômé en Mai 2024.")
    assert "2026" in extraire_dates("Projet lancé en 2026.")


# ---------- heuristiques ----------
def test_nom_candidat_premiere_ligne():
    texte = "IHEB KHALDI\nBusiness Intelligence & Data Analysis\nAriana, Tunisie"
    assert extraire_nom_candidat(texte) == "Iheb Khaldi"


def test_nom_candidat_ignore_titre_section():
    texte = "COMPÉTENCES CLÉS\nJean Dupont\nParis"
    assert extraire_nom_candidat(texte) == "Jean Dupont"


def test_dedupe_insensible_casse():
    assert dedupe(["Python", "python", " PYTHON "]) == ["Python"]
