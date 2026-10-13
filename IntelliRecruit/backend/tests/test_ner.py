# -*- coding: utf-8 -*-
"""Tests S4 — A2 : NER spaCy avancé multi-langue (fr/en avec fallback)."""
from app.services.cv_intelligence.ner import extraire_entites_avancees, get_nlp


def test_structure_de_sortie():
    """Le format de sortie est celui du contrat S1/S2 (6 clés)."""
    entites = extraire_entites_avancees("Jean Dupont travaille à Tunis.", "fr")
    for cle in ("personnes", "organisations", "lieux", "emails", "telephones", "dates"):
        assert cle in entites


def test_regex_fiables_conservees():
    """Emails / téléphones / dates restent extraits par regex (logique S1)."""
    entites = extraire_entites_avancees(
        "Contact : jean@mail.tn, +216 21 094 951, diplômé en Mai 2024.", "fr"
    )
    assert entites["emails"] == ["jean@mail.tn"]
    assert "+216 21 094 951" in entites["telephones"]
    assert "Mai 2024" in entites["dates"]


def test_fallback_langue_inconnue():
    """Langue None ou modèle absent -> on retombe sur le modèle français
    au lieu de planter (le CV est quand même parsé)."""
    nlp = get_nlp(None)
    assert nlp is not None
    nlp_ar = get_nlp("ar")  # pas de modèle arabe -> fallback fr
    assert nlp_ar is not None
