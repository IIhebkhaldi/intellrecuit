# Vérité terrain du mini-dataset (`data/sample_cvs/`)

Valeurs attendues pour chaque CV de test — base du futur dataset annoté de
100+ CVs (livrable Module A) et du calcul precision/recall en S6.

## Identité (S3)

| Fichier | Format | Langue | Prénom | Nom | Email | Téléphone |
|---|---|---|---|---|---|---|
| cv_amira_bensalem.pdf | pdf | fr | Amira | Ben Salem | amira.bensalem@gmail.com | +216 22 345 678 |
| cv_john_smith.pdf | pdf | en | John | Smith | john.smith@outlook.com | +44 20 7946 0958 |
| cv_lina_kacem.pdf | pdf | fr | Lina | Kacem | lina.kacem@etudiant.esprit.tn | *(aucun)* |
| cv_mohamed_trabelsi.docx | docx | fr | Mohamed | Trabelsi | mohamed.trabelsi@yahoo.fr | +216 98 765 432 |
| cv_sara_gharbi.docx | docx | en | Sara | Gharbi | sara.gharbi@protonmail.com | +33 6 12 34 56 78 |
| cv_youssef_benali.txt | txt | fr | Youssef | Ben Ali | youssef.benali@hotmail.com | 55 123 456 |

Bonus : `location` (ex : "Ariana, Tunisie") et `linkedin`.
`cv_lina_kacem.pdf` = cas limite (pas de téléphone ni LinkedIn → `null`).

## Structuration (S4)

Nombre d'items attendu par section :

| Fichier | Expériences | Formations | Skills | Langues | Certifs |
|---|---|---|---|---|---|
| cv_amira_bensalem.pdf | 1 | 1 | 6 | 3 | 2 |
| cv_john_smith.pdf | 1 | 1 | 5 | 2 | 1 |
| cv_lina_kacem.pdf | 0 | 1 | 3 | 3 | 0 |
| cv_mohamed_trabelsi.docx | 1 | 1 | 5 | 3 | 0 |
| cv_sara_gharbi.docx | 1 | 1 | 7 | 3 | 0 |
| cv_youssef_benali.txt | 1 | 1 | 9 | 3 | 0 |

Exemples de valeurs attendues (Amira) :
- **Expérience** : `Stage Data Analyst` @ `Vermeg`, `2025-06` → `2025-08`
- **Formation** : `Ingénieur Informatique`, spécialité `Data & IA`, `ESPRIT`, 2022–2025
- **Skills normalisés** : python (language), sql (database), power bi (tool)...
- **Langues** : arabic=native, french=fluent, english=professional

Convention dates (J10) : `"YYYY-MM"` (ou `"YYYY"` si mois inconnu) ;
poste actuel → `end_date = null`.
