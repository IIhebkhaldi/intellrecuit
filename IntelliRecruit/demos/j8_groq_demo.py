# -*- coding: utf-8 -*-
"""
J8 — Démo autonome : LLM Groq + prompt engineering.

Prérequis : copie .env.example en .env et renseigne GROQ_API_KEY
            (clé partagée fournie par l'encadrant).
Lancer :   python demos/j8_groq_demo.py
"""
import json
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from groq import Groq

api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    raise SystemExit("❌ GROQ_API_KEY absente. Copie .env.example en .env et mets la clé.")

client = Groq(api_key=api_key)
MODELE = "llama-3.3-70b-versatile"

profil = ("Iheb Khaldi, étudiant ingénieur BI à ESPRIT Tunis. Stage data science à "
          "Tunisie Télécom (analyse trafic/QoS, modèles ML). Projets : Scout Analytics "
          "(DW, SSIS, Power BI), comparateur de prix temps réel, churn ML. "
          "Compétences : Python, SQL, Power BI, Talend, scikit-learn.")

# ---------------------------------------------------------------
# Technique 1 : rôle système + température basse
# ---------------------------------------------------------------
r1 = client.chat.completions.create(
    model=MODELE,
    messages=[
        {"role": "system", "content": "Tu es un assistant RH. Réponds en français, en 2 phrases maximum."},
        {"role": "user", "content": f"Résume ce profil : {profil}"},
    ],
    temperature=0.3,
)
print("=== 1) Rôle système ===")
print(r1.choices[0].message.content, "\n")

# ---------------------------------------------------------------
# Technique 2 : few-shot (on montre le format attendu par l'exemple)
# ---------------------------------------------------------------
r2 = client.chat.completions.create(
    model=MODELE,
    messages=[
        {"role": "system", "content": "Tu classes des compétences par catégorie."},
        {"role": "user", "content": "Compétence : Python"},
        {"role": "assistant", "content": "language"},
        {"role": "user", "content": "Compétence : PostgreSQL"},
        {"role": "assistant", "content": "database"},
        {"role": "user", "content": "Compétence : Power BI"},
    ],
    temperature=0,
)
print("=== 2) Few-shot (catégorie de 'Power BI') ===")
print(r2.choices[0].message.content, "\n")

# ---------------------------------------------------------------
# Technique 3 : sortie JSON forcée + parsing défensif
# ---------------------------------------------------------------
prompt_json = (
    "Extrais les informations de ce profil. Réponds UNIQUEMENT avec un JSON valide, "
    "sans texte autour, sans markdown, au format exact :\n"
    '{"nom": "...", "competences": ["..."], "annees_experience": 0}\n\n'
    f"Profil : {profil}"
)
r3 = client.chat.completions.create(
    model=MODELE,
    messages=[{"role": "user", "content": prompt_json}],
    temperature=0,
)
brut = r3.choices[0].message.content.strip().replace("```json", "").replace("```", "").strip()
print("=== 3) Sortie JSON forcée ===")
try:
    data = json.loads(brut)
    print(json.dumps(data, indent=2, ensure_ascii=False))
    print("\nParsing JSON réussi ✅ — type :", type(data).__name__)
except json.JSONDecodeError:
    print("⚠️ Le LLM n'a pas renvoyé un JSON valide (edge case à gérer !) :\n", brut)
