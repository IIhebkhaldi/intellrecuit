# Rapport de métriques — Module A (S6, mis à jour S7/S8)

**Objectif du cahier (O2)** : ≥ 85 % de precision sur **nom, email, skills**.
Mesuré avec `python demos/s6_evaluation_demo.py` sur le dataset annoté
`data/ground_truth.json` (**100 CVs**, généré par `data/generer_cvs_test.py`).

## Résultats (100 CVs annotés)

| Champ | Precision | Recall | F1 |
|---|---|---|---|
| first_name | 100 % | 100 % | 1.00 |
| last_name | 100 % | 100 % | 1.00 |
| email | 100 % | 100 % | 1.00 |
| phone | 100 % | 100 % | 1.00 |
| location | 100 % | 100 % | 1.00 |
| linkedin | 100 % | 100 % | 1.00 |
| language | 100 % | 100 % | 1.00 |
| **skills** | **100 %** | **100 %** | **1.00** |
| languages | 100 % | 100 % | 1.00 |

**Objectif O2 (nom + email + skills)** : precision **100 %**, recall **100 %** →
✅ **cible ≥ 85 % largement atteinte**.

## Évolution

| Version | Dataset | Precision skills | O2 |
|---|---|---|---|
| S6 initiale | 6 CVs | 86 % | 91 % |
| + fix dédoublonnage d'alias | 6 CVs | 88 % | 92 % |
| + dataset élargi (S7) | 30 CVs | 96 % | 98 % |
| **+ scan ciblé + 100 CVs (S8)** | **100 CVs** | **100 %** | **100 %** |

### Ce qui a été amélioré

1. **Dédoublonnage d'alias chevauchants** (S7) : dans « SQL Server », on ne
   compte plus `sql` en double. Déduplication **par position** dans
   `skills_extractor.extraire_skills_texte`.
2. **Dataset 6 → 30 → 100 CVs** : générateur `generer_cvs_test.py` **piloté par
   les données** — le CV et son annotation viennent de la même source, donc
   toujours cohérents. 10 métiers, 3 formats (PDF/DOCX/TXT), FR + EN, noms
   tunisiens et internationaux.
3. **Scan des skills ciblé sur les bonnes sources** (fix précision → 100 %) :
   les skills sont extraits de la **section Compétences** (déclaratif) et des
   **descriptions d'expérience** (usage concret), mais **plus du document
   entier**. Un skill présent seulement dans un **intitulé de poste**
   (« Ingénieur Machine Learning ») ou une **spécialité de formation**
   (« spécialité Business Intelligence ») n'est plus compté comme compétence
   déclarée — c'était la source des 6 derniers faux positifs.

## Pourquoi ce choix (à savoir expliquer)

Un intitulé de poste ou une spécialité de diplôme n'est pas une **compétence
déclarée** par le candidat : le compter gonflait la liste de skills avec des
faux positifs. En restreignant le scan aux deux sources fiables (section
Compétences + descriptions d'expérience), on aligne l'extraction sur la
définition de la vérité terrain → precision **100 %** sans perdre de recall
(les vrais skills restent dans ces deux sources).

## Pistes suivantes

1. **Agrandir encore** : viser 100+ CVs, idéalement de **vrais CVs anonymisés**.
2. **Tester sur des CVs réels non structurés** (multi-colonnes) — c'est là que
   la précision baissera vraiment (défi S8).
3. **Pondérer par source** : skill de la section Compétences = confiance haute ;
   skill vu seulement dans une description = confiance moyenne (champ `source`).

## Reproduire

```bash
python data/generer_cvs_test.py     # (re)génère les 100 CVs + ground_truth.json
python demos/s6_evaluation_demo.py  # affiche le rapport P/R
cd backend && pytest tests/test_evaluation.py tests/test_skills.py -v
```
Ou dans le frontend : page **Metriques** (http://localhost:8501).
