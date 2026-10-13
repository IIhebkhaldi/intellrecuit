# CONTEXTE PROJET — à lire en premier (reprise de travail)

> Document de passation. Contient **tout** ce qu'il faut pour reprendre le
> travail sans historique de conversation.
> Dernière mise à jour : **24 juillet 2026**

---

## 1. QUI / QUOI

| | |
|---|---|
| **Projet** | IntelliRecruit — plateforme IA de recrutement |
| **Entreprise** | ADDINN Group — Département Data & IA |
| **Stage** | Été 2026, 8 semaines, trinôme |
| **Encadrant** | Baha Rahmouni — baha.rahmouni@addinn.com |
| **Moi** | **Stagiaire 1 — Module A : CV Intelligence Engine** |
| **Binôme B** | Mohamed — Module B (Job Matching & Ranking) |
| **Binôme C** | Amen Allah — Module C (Recruiter Assistant & Analytics) |
| **Cahier des charges** | `C:\Users\lenovo\Downloads\Cahier_de_Charges.pdf` |
| **Langue de travail** | Français |

**Mon module (A)** : transformer un fichier CV (PDF/DOCX/TXT) en JSON structuré
`CVData` — le contrat commun consommé par les modules B et C.

---

## 2. OÙ EST LE PROJET

```
C:\Users\lenovo\Downloads\IntelliRecruit        ← LE PROJET (unique)
```

⚠️ **Un seul projet**, pas un dossier par semaine. Chaque semaine = des commits
dans ce même dépôt. Les anciens dossiers `intellirecruit-semaine2/3/4` dans
`C:\Users\lenovo\Downloads\` sont **périmés** — ne pas les utiliser.

### Structure (conforme Annexe E du cahier)

```
IntelliRecruit/
├── backend/
│   ├── app/
│   │   ├── main.py                       # uvicorn app.main:app  (v0.5.0)
│   │   ├── config.py                     # RACINE_REPO, .env
│   │   ├── api/
│   │   │   ├── cvs.py                    # /api/cv/*  (+ /api/cv/metrics)
│   │   │   ├── jobs.py                   # /api/jobs/* (offres, commun)
│   │   │   └── pipeline.py               # /api/pipeline (exercice S2)
│   │   ├── services/
│   │   │   ├── cv_intelligence/          # ⭐ LE MODULE A
│   │   │   │   ├── parser.py             #   A1 dispatch multi-format
│   │   │   │   ├── pdf_parser.py         #   A1 PDF (pypdf + pdfplumber)
│   │   │   │   ├── docx_parser.py        #   A1 DOCX
│   │   │   │   ├── language_detector.py  #   A1 langue fr/en/ar
│   │   │   │   ├── identity_parser.py    #   nom/email/tél/localisation/linkedin
│   │   │   │   ├── ner.py                #   A2 NER spaCy fr/en
│   │   │   │   ├── section_detector.py   #   A3 sections
│   │   │   │   ├── experience_parser.py  #   A3 expériences + dates
│   │   │   │   ├── education_parser.py   #   A3 formations
│   │   │   │   ├── languages_parser.py   #   A3 langues + certifications
│   │   │   │   ├── skills_normalizer.py  #   A4 ontologie ~90 skills + fuzzy
│   │   │   │   ├── skills_extractor.py   #   A4 extraction skills
│   │   │   │   ├── cv_service.py         #   orchestrateur parse_cv()
│   │   │   │   └── evaluation.py         #   S6 métriques precision/recall
│   │   │   ├── parsing.py                # briques bas niveau (regex, nettoyage)
│   │   │   ├── embeddings.py / llm.py    # parts binômes (S2, optionnels)
│   │   ├── schemas/shared.py             # ⭐ CONTRAT : CVData, JobData, MatchResult
│   │   └── db/                           # SQLAlchemy : database.py, models.py, crud.py
│   ├── tests/                            # 99 tests pytest
│   └── requirements.txt
├── frontend/
│   ├── streamlit_app.py
│   └── pages/{1_Upload_CVs.py, 2_Resultats.py, 3_Metriques.py}
├── data/
│   ├── sample_cvs/                       # 100 CVs de test (pdf/docx/txt, fr/en)
│   ├── ground_truth.json                 # vérité terrain annotée (S6)
│   ├── generer_cvs_test.py
│   ├── verite_terrain.md
│   └── rapport_metriques_s6.md
├── demos/
│   ├── s3_parsing_demo.py                # identité
│   ├── s4_module_demo.py                 # CVData complet
│   ├── s5_pipeline_demo.py               # pipeline A→B→C (stubs B/C)
│   └── s6_evaluation_demo.py             # ⭐ rapport precision/recall
├── venv/                                 # environnement Python (gitignored)
└── CONTEXTE_PROJET.md                    # CE FICHIER
```

---

## 3. ENVIRONNEMENT — IMPORTANT

**venv du projet** : `C:\Users\lenovo\Downloads\IntelliRecruit\venv` (Python **3.14**)

Contient : fastapi, uvicorn, pydantic, python-multipart, sqlalchemy, pypdf,
pdfplumber, python-docx, langdetect, fpdf2, spacy (+ modèles **fr_core_news_sm**
et **en_core_web_sm**), streamlit, requests, pandas, pytest, httpx, python-dotenv.

### ⚠️ Pièges connus

1. **NE PAS installer `sentence-transformers`** → il tire **torch** (~2 Go) dont les
   chemins dépassent la limite Windows de 260 caractères → `[WinError 206]`.
   Ces libs (sentence-transformers, chromadb, groq) sont **commentées** dans
   `backend/requirements.txt`. Le Module A fonctionne parfaitement sans.
2. **Console Windows en cp1252** → les `print()` avec accents plantent. Tous les
   scripts de démo utilisent :
   ```python
   import io, sys
   sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
   ```
3. **Le terminal de l'utilisateur est PowerShell** (pas bash) : utiliser `curl.exe`
   (pas `curl`), et `;` au lieu de `&&`.

---

## 4. COMMANDES

```powershell
cd C:\Users\lenovo\Downloads\IntelliRecruit
.\venv\Scripts\activate
```

| Action | Commande |
|---|---|
| **Backend** (terminal 1) | `cd backend` puis `uvicorn app.main:app --reload` → http://localhost:8000/docs |
| **Frontend** (terminal 2) | `streamlit run frontend/streamlit_app.py` → http://localhost:8501 |
| **Tests** | `cd backend` puis `python -m pytest tests -q` → **99 passed** |
| **Démo S6 (métriques)** | `python demos/s6_evaluation_demo.py` |
| **Démo S4 (CVData)** | `python demos/s4_module_demo.py` |
| **Démo S5 (pipeline)** | `python demos/s5_pipeline_demo.py` |
| **Git** | `git add .` ; `git commit -m "feat(module-a): ..."` ; `git push` |

Si un port est occupé : `netstat -ano | findstr ":8000"` puis
`Stop-Process -Id <PID> -Force`.

---

## 5. CE QUI EST FAIT (S3 → S6)

**7 commits sur la branche `feature/module-a`, tout poussé sur GitLab.**

### S3 — Parsing multi-format + identité
PDF (pypdf + fallback pdfplumber), DOCX (paragraphes **et** tableaux), TXT.
Extraction : prénom, nom, email, téléphone, localisation, LinkedIn.
Détection de langue fr/en/ar.

### S4 — NER + structuration + normalisation skills
- **A2** : NER spaCy multi-langue (le modèle suit la langue détectée, fallback fr)
- **A3** : détection des sections + découpage en items (expériences avec dates
  `YYYY-MM`, formations, langues, certifications)
- **A4** : ontologie ~90 skills + fuzzy matching (difflib, seuil 0.85) →
  « Python 3 », « sklearn », « postgress » → skill canonique catégorisé

### S5 (partie solo) — Persistance + offres + pipeline
- `db/` SQLAlchemy : tables `cvs` et `jobs` (SQLite en dev), **anti-doublon par
  hash sha256**
- `/api/jobs/*` : CRUD des offres (F1) + `JobData`/`JobCreate`/`MatchResult`
  ajoutés au contrat partagé
- `demos/s5_pipeline_demo.py` : pipeline bout-en-bout **avec des STUBS** pour les
  modules B et C

### S6 — Precision / Recall
- `evaluation.py` : métriques P/R/F1 par champ (valeurs simples + listes)
- `data/ground_truth.json` : vérité terrain annotée (100 CVs)
- `demos/s6_evaluation_demo.py` + endpoint `GET /api/cv/metrics` + page
  Streamlit **« Metriques »**

**Résultats mesurés (dataset à 100 CVs — exigence cahier §5.1 atteinte)** :
| Champ | Precision | Recall |
|---|---|---|
| nom, email, téléphone, localisation, LinkedIn, langue | **100 %** | 100 % |
| **skills** | **100 %** | 100 % |

→ **Objectif O2 (nom + email + skills) : precision 100 %, recall 100 % — cible ≥ 85 % ✅ ATTEINTE**

**Améliorations successives (retour encadrant)** : (1) dédoublonnage d'alias
chevauchants (`sql` vs `sql server`) → skills 86 %→96 % ; (2) dataset 6→30→70→**100
CVs** via un générateur piloté par les données (`data/generer_cvs_test.py`
produit les CVs **et** `ground_truth.json`) ; (3) **scan des skills ciblé** sur
la section Compétences + les descriptions d'expérience (plus le document entier)
→ un skill vu seulement dans un intitulé de poste (« Ingénieur Machine
Learning ») ou une spécialité de diplôme n'est plus un faux positif → skills
96 %→**100 %**. Détails : `data/rapport_metriques_s6.md`.

---

## 6. GITLAB (dépôt d'équipe)

**URL** :
```
https://code.addinn-group.com/addinn/digital-software-factory/stage-lab/stage_ete/2026/data-ai/sujet-4-intellirecruit/intellirecruit.git
```
Project ID **2179**. Je suis **Developer**. Ma branche : **`feature/module-a`**.

### ⚠️ Config réseau OBLIGATOIRE
Le serveur n'est joignable **qu'à travers le proxy SOCKS du VPN** :
```
git config http.proxy socks5h://127.0.0.1:23321
```
(déjà configuré dans le dépôt). **Le VPN doit tourner**, sinon
`Could not connect to server`. Si le port du VPN change, mettre à jour cette config.

### ⚠️ Authentification
Git Credential Manager **ne gère pas** le proxy SOCKS → la fenêtre d'identification
ne s'ouvre pas. Solution en place : **le token est dans l'URL du remote**
(`https://<user>:<token>@code.addinn-group.com/...`).

🔴 **À FAIRE** : le token a été exposé en clair → **le régénérer** sur GitLab
(Access Tokens → supprimer → créer un nouveau avec `write_repository`) puis
`git remote set-url origin "https://<user>:<nouveau_token>@code.addinn-group.com/..."`.

### Workflow Git du projet (cahier §12.4)
`feature/module-a` (moi) → **Merge Request** → `develop` → `main` (validé par l'encadrant).
Convention de commit : `feat(module-a): description`.
❌ Ne **jamais** pousser sur `main` (protégée), ❌ **jamais** de `git push -f`.

---

## 7. ÉTAT DE L'ÉQUIPE (constaté le 24/07/2026)

| Branche | Qui | Contenu réel | État |
|---|---|---|---|
| `feature/module-a` | Moi | Structure Annexe E complète, contrat `shared.py`, `db/`, 99 tests | ✅ **le plus avancé** |
| `feature/module-c` | Amen Allah | `api/assistant.py`, services (questions, grille, RAG), son propre `main.py`, tests | 🟡 avancé **mais PAS de `schemas/shared.py`** → n'utilise pas le contrat commun |
| `feature/module-b` | Mohamed | **seulement** `parse_cv_spacy.py` + des CV PDF à la racine | 🔴 **le matching n'existe pas** |
| `main` | commun | juste un README (Initial commit) | protégée |

**Il n'y a PAS de branche `develop`.**

---

## 8. CE QU'IL RESTE À FAIRE

### 🔴 S5 — Intégration (INCOMPLÈTE, bloquée sur l'équipe)
Le livrable S5 = *« backend FastAPI unifié + pipeline complet fonctionnel en local »*.
Manque :
1. **Le Module B (matching) de Mohamed** — c'est le maillon central `parse → MATCH → questions`
2. **Une branche `develop`** où fusionner les 3 modules
3. **Le contrat `schemas/shared.py` adopté par B et C** (seul le Module A l'utilise)
4. **Un seul `main.py` unifié** incluant les 3 routers (il y en a 2 aujourd'hui)

**Piste envisagée (non réalisée)** : construire une **base d'intégration** sur une
branche `develop` = Module A (réel) + un matching **simple mots-clés temporaire** +
l'assistant, tous sur le contrat commun → donne un pipeline qui tourne, à présenter
comme **proposition** au point d'intégration du mercredi (Mohamed et Amen
remplaceraient ensuite par leurs vrais modules).

### ⏳ S7 — Frontend Streamlit commun (5 pages) — **nécessite l'intégration S5**
### ⏳ S8 — Docker + docker-compose + déploiement + démo — **nécessite tout le reste**

### ✅ Ce qui n'est PAS bloqué
Le travail solo du Module A peut continuer : **étendre le dataset annoté vers
100+ CVs** (livrable clé du Module A) et améliorer la précision des skills.

---

## 9. DÉCISIONS TECHNIQUES À SAVOIR EXPLIQUER

> Le cahier prévient : *« Vous devez comprendre chaque ligne de votre code. »*

- **Ontologie + fuzzy plutôt qu'un NER custom entraîné** : un NER custom exige un
  dataset annoté qu'on n'aura qu'après ; l'ontologie est fiable et **explicable**
  tout de suite. Seuil fuzzy élevé (0.85) : on préfère rater un skill qu'en inventer un.
- **Dates en regex, pas en NER** : le NER rate souvent les plages
  (« Juin 2025 - Août 2025 ») ; la regex produit directement le format `YYYY-MM`.
- **Détection de langue « maison »** (vote de mots-outils « de/et/chez » vs
  « the/of/with » + accents) : un CV est plein de termes techniques anglais qui
  trompent `langdetect`.
- **Fallback pdfplumber** : si l'extraction pypdf est « suspecte » (pas de saut de
  ligne, aucun email), on retente avec pdfplumber qui respecte mieux l'ordre visuel.
- **Convention J10** : champ introuvable = `None`, listes vides = `[]`, poste
  actuel = `end_date: null`, entreprise non détectée = `"?"` (réparée par le NER).
- **`level` des skills = `null`** : non déductible de façon fiable sans annotation
  (décision assumée, pas un oubli).

---

## 10. BUGS DÉJÀ CORRIGÉS (ne pas les refaire)

| Problème | Solution appliquée |
|---|---|
| Téléphone français tronqué | regex `\d{1,4}` au lieu de `\d{2,4}` |
| Localisation débordant sur la ligne précédente | recherche **ligne par ligne** |
| Nom = « Développeur Web Professionnel » | liste `_MOTS_A_IGNORER` de titres de métier |
| Nom en MAJUSCULES | `.title()` |
| « Ben Ali » tronqué | abandon de spaCy pour le nom, heuristique ligne + filtre métiers |
| Langue « de »/« ca » sur un CV français | détection par mots-outils |
| Spécialité avalant le nom d'école | regex lazy `+?` + lookahead |
| « de Juin 2025 à Août 2025 » non détecté | `\ba\b` (le texte est désaccentué avant la regex) |
| `/api/cv/metrics` capté par `/{cv_id}` | route `/metrics` déclarée **avant** `/{cv_id}` |
| `pip install` échoue sur torch | ne pas installer sentence-transformers |

---

## 11. LIMITES CONNUES (à assumer en démo)

1. Les résultats parfaits sont sur des **CVs bien structurés** (générés). Un CV
   design multi-colonnes casse le découpage en sections (texte PDF mélangé).
   L'endpoint `POST /api/cv/debug` montre le texte brut extrait pour diagnostiquer.
2. Les **templates Canva non remplis** contiennent des placeholders
   (`hello@reallygreatsite.com`) que le parser extrait fidèlement — aucun outil ne
   peut deviner des données absentes.
3. Le dataset annoté fait **100 CVs** (générés) → exigence cahier §5.1 (100+)
   atteinte. Amélioration future : compléter avec de **vrais CVs anonymisés**
   (les CVs générés sont bien structurés ; un vrai CV design multi-colonnes
   reste plus difficile — cf. limite n°1).
