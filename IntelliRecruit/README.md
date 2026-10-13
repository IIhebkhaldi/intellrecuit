# IntelliRecruit — Module A : CV Intelligence Engine

Stagiaire : **Iheb Khaldi** (Stagiaire 1) — ADDINN Group — Stage d'été 2026

Projet **unique et évolutif** (pas un dossier par semaine) : chaque semaine
ajoute des fonctionnalités **dans ce même code**, tracées par les commits Git.
Structure conforme à l'**Annexe E** du cahier des charges.

Le Module A transforme un fichier CV (**PDF / DOCX / TXT**) en JSON structuré
**`CVData`** — le contrat commun (J10) consommé par le Module B (matching,
Mohamed) et le Module C (assistant, Amen Allah).

---

## 🗺️ Évolution du module (historique = commits Git)

| Semaine | Ajout dans ce projet |
|---|---|
| **S2** | Structure FastAPI + schemas `CVData` + endpoints |
| **S3** | Parsing PDF/DOCX/TXT + extraction identité (nom, email, téléphone) |
| **S4** | NER spaCy multi-langue + structuration (exp/formation/langues) + normalisation skills |
| S5→ | Intégration inter-modules, base PostgreSQL, Docker, déploiement |

---

## 📁 Structure (Annexe E)

```
IntelliRecruit/
├── backend/
│   ├── app/
│   │   ├── main.py                       # app FastAPI (uvicorn app.main:app)
│   │   ├── config.py                     # chargement .env
│   │   ├── api/
│   │   │   ├── cvs.py                     # endpoints /api/cv/*  (Module A)
│   │   │   └── pipeline.py               # /api/pipeline (exercice S2)
│   │   ├── services/
│   │   │   ├── cv_intelligence/          # ⭐ LE MODULE A (découpé par responsabilité)
│   │   │   │   ├── parser.py             #   A1  dispatch multi-format
│   │   │   │   ├── pdf_parser.py         #   A1  PDF (pypdf + pdfplumber)
│   │   │   │   ├── docx_parser.py        #   A1  DOCX (paragraphes + tableaux)
│   │   │   │   ├── language_detector.py  #   A1  langue fr/en/ar
│   │   │   │   ├── identity_parser.py    #   nom, email, téléphone, localisation, linkedin
│   │   │   │   ├── ner.py                #   A2  NER spaCy multi-langue
│   │   │   │   ├── section_detector.py   #   A3  détection + découpage des sections
│   │   │   │   ├── experience_parser.py  #   A3  expériences + parsing des dates
│   │   │   │   ├── education_parser.py   #   A3  formations
│   │   │   │   ├── languages_parser.py   #   A3  langues + certifications
│   │   │   │   ├── skills_normalizer.py  #   A4  ontologie + normalisation (fuzzy)
│   │   │   │   ├── skills_extractor.py   #   A4  extraction des skills
│   │   │   │   └── cv_service.py         #   orchestrateur -> CVData complet
│   │   │   ├── parsing.py                # briques bas niveau (regex, nettoyage)
│   │   │   ├── embeddings.py / llm.py    # parts Mohamed / Amen Allah (S2)
│   │   │   └── ...
│   │   └── schemas/shared.py             # CVData, JobData, MatchResult (contrat J10)
│   ├── tests/                            # 77 tests pytest
│   └── requirements.txt
├── frontend/
│   ├── streamlit_app.py
│   ├── pages/{1_Upload_CVs.py, 2_Resultats.py}
│   └── requirements.txt
├── data/
│   ├── sample_cvs/                       # 6 CVs de test (pdf/docx/txt, fr/en)
│   ├── generer_cvs_test.py
│   └── verite_terrain.md
├── demos/                                # scripts de démonstration
├── requirements.txt                      # méta : backend + frontend
├── .env.example
├── .gitignore
└── README.md
```

À venir (semaines prévues) : `backend/app/db/` (PostgreSQL, S5),
`Dockerfile` + `docker-compose.yml` (S8), `docs/` (S8).

---

## 🚀 Installation

```powershell
cd C:\Users\lenovo\Downloads\IntelliRecruit
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download fr_core_news_sm
python -m spacy download en_core_web_sm
```

> ⚠️ `sentence-transformers` (torch) est **volontairement exclu** :
> ses chemins dépassent la limite Windows de 260 caractères. Le Module A
> fonctionne sans. Il n'est utile qu'au pipeline S2 (`/api/pipeline`).

---

## ▶️ Lancer le projet

**Backend** (terminal 1) :
```powershell
cd backend
uvicorn app.main:app --reload
```
→ Swagger : http://localhost:8000/docs · Health : http://localhost:8000/health

**Frontend** (terminal 2) :
```powershell
streamlit run frontend/streamlit_app.py
```
→ http://localhost:8501

**Démo CLI** (sans serveur) :
```powershell
python demos/s4_module_demo.py
```

**Tests** :
```powershell
cd backend
pytest tests -v          # 77 tests
```

---

## 🔌 API du Module A

| Méthode | Endpoint | Rôle |
|---|---|---|
| POST | `/api/cv/parse` | 1 fichier → `CVData` complet |
| POST | `/api/cv/batch` | plusieurs fichiers → liste de `CVData` |
| GET | `/api/cv/{id}` | relire un CV parsé |
| POST | `/api/cv/debug` | texte brut extrait (diagnostic) |

---

## ⚠️ Limites connues

- Les résultats parfaits sont sur des CVs **bien structurés**. Un CV design
  multi-colonnes casse le découpage en sections (texte PDF mélangé).
- `level` des skills = `null` (non déductible de façon fiable sans annotation).
- Stockage des CVs **en mémoire** (dict) ; la table PostgreSQL `cvs` arrive en S5.

Prochaine étape (S5) : intégration inter-modules — ce `CVData` alimente le
matching du Module B et l'assistant du Module C.
