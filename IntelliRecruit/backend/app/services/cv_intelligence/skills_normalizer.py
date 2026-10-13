# -*- coding: utf-8 -*-
"""
Normalisation des compétences — cahier des charges §5.1 (A4).

- Ontologie de compétences (skill canonique -> catégorie + alias)
- "Python 3", "python", "Python programming" -> même skill "python"
- Fuzzy matching (difflib, biblio standard) pour tolérer les fautes de frappe

Catégories du cahier : language / framework / cloud / database / methodology,
complétées par tool et data.
"""
import re
from difflib import get_close_matches
from typing import Optional

ONTOLOGIE: dict[str, tuple[str, list[str]]] = {
    # --- Langages ---
    "python":       ("language", ["python", "python 3", "python3", "python programming", "python avancé"]),
    "java":         ("language", ["java", "java se", "java ee", "jee", "j2ee"]),
    "javascript":   ("language", ["javascript", "js", "ecmascript", "es6"]),
    "typescript":   ("language", ["typescript", "ts"]),
    "c":            ("language", ["c"]),
    "c++":          ("language", ["c++", "cpp", "c plus plus"]),
    "c#":           ("language", ["c#", "csharp", "c sharp"]),
    "php":          ("language", ["php"]),
    "r":            ("language", ["r"]),
    "go":           ("language", ["go", "golang"]),
    "kotlin":       ("language", ["kotlin"]),
    "swift":        ("language", ["swift"]),
    "scala":        ("language", ["scala"]),
    "matlab":       ("language", ["matlab"]),
    "bash":         ("language", ["bash", "shell", "shell scripting"]),
    # --- Frameworks / librairies ---
    "django":       ("framework", ["django"]),
    "flask":        ("framework", ["flask"]),
    "fastapi":      ("framework", ["fastapi", "fast api"]),
    "spring":       ("framework", ["spring", "spring boot", "springboot"]),
    "react":        ("framework", ["react", "reactjs", "react.js", "react js"]),
    "angular":      ("framework", ["angular", "angularjs"]),
    "vue":          ("framework", ["vue", "vuejs", "vue.js"]),
    "node.js":      ("framework", ["node.js", "node", "nodejs", "node js"]),
    "laravel":      ("framework", ["laravel"]),
    "symfony":      ("framework", ["symfony"]),
    ".net":         ("framework", [".net", "dotnet", "asp.net"]),
    "streamlit":    ("framework", ["streamlit"]),
    "tensorflow":   ("framework", ["tensorflow", "tensor flow"]),
    "keras":        ("framework", ["keras"]),
    "pytorch":      ("framework", ["pytorch", "torch"]),
    "scikit-learn": ("framework", ["scikit-learn", "sklearn", "scikit learn", "scikitlearn"]),
    "pandas":       ("framework", ["pandas"]),
    "numpy":        ("framework", ["numpy"]),
    "spacy":        ("framework", ["spacy"]),
    "opencv":       ("framework", ["opencv", "open cv"]),
    # --- Cloud / conteneurs ---
    "aws":          ("cloud", ["aws", "amazon web services"]),
    "azure":        ("cloud", ["azure", "microsoft azure"]),
    "gcp":          ("cloud", ["gcp", "google cloud", "google cloud platform"]),
    "docker":       ("cloud", ["docker"]),
    "kubernetes":   ("cloud", ["kubernetes", "k8s"]),
    "terraform":    ("cloud", ["terraform"]),
    # --- Bases de données ---
    "sql":          ("database", ["sql", "requêtes sql", "sql queries"]),
    "mysql":        ("database", ["mysql", "my sql"]),
    "postgresql":   ("database", ["postgresql", "postgres", "postgre sql"]),
    "mongodb":      ("database", ["mongodb", "mongo", "mongo db"]),
    "oracle":       ("database", ["oracle", "oracle db"]),
    "sql server":   ("database", ["sql server", "sqlserver", "mssql", "microsoft sql server"]),
    "sqlite":       ("database", ["sqlite"]),
    "redis":        ("database", ["redis"]),
    "elasticsearch": ("database", ["elasticsearch", "elastic search"]),
    "chromadb":     ("database", ["chromadb", "chroma db", "chroma"]),
    "snowflake":    ("database", ["snowflake"]),
    # --- Méthodologies / concepts ---
    "agile":        ("methodology", ["agile", "méthode agile", "agilité"]),
    "scrum":        ("methodology", ["scrum"]),
    "kanban":       ("methodology", ["kanban"]),
    "crisp-dm":     ("methodology", ["crisp-dm", "crisp dm", "crispdm"]),
    "devops":       ("methodology", ["devops", "dev ops"]),
    "ci/cd":        ("methodology", ["ci/cd", "cicd", "ci cd", "intégration continue"]),
    "uml":          ("methodology", ["uml"]),
    "etl":          ("methodology", ["etl", "pipelines etl", "pipeline etl"]),
    # --- Data / IA ---
    "machine learning": ("data", ["machine learning", "ml", "apprentissage automatique"]),
    "deep learning":    ("data", ["deep learning", "apprentissage profond"]),
    "nlp":              ("data", ["nlp", "natural language processing", "traitement du langage"]),
    "computer vision":  ("data", ["computer vision", "vision par ordinateur"]),
    "data analysis":    ("data", ["data analysis", "analyse de données", "analyse de donnees"]),
    "business intelligence": ("data", ["business intelligence", "bi"]),
    "data warehousing": ("data", ["data warehousing", "data warehouse", "entrepôt de données"]),
    "mlops":            ("data", ["mlops", "ml ops"]),
    # --- Outils ---
    "power bi":     ("tool", ["power bi", "powerbi", "power_bi", "microsoft power bi"]),
    "tableau":      ("tool", ["tableau", "tableau software"]),
    "excel":        ("tool", ["excel", "microsoft excel", "ms excel"]),
    "git":          ("tool", ["git", "versioning git"]),
    "github":       ("tool", ["github", "git hub"]),
    "gitlab":       ("tool", ["gitlab", "git lab"]),
    "jira":         ("tool", ["jira"]),
    "talend":       ("tool", ["talend"]),
    "ssis":         ("tool", ["ssis"]),
    "ssas":         ("tool", ["ssas"]),
    "dax":          ("tool", ["dax"]),
    "power query":  ("tool", ["power query", "powerquery"]),
    "airflow":      ("tool", ["airflow", "apache airflow"]),
    "spark":        ("tool", ["spark", "apache spark", "pyspark"]),
    "hadoop":       ("tool", ["hadoop"]),
    "kafka":        ("tool", ["kafka", "apache kafka"]),
    "linux":        ("tool", ["linux", "gnu/linux"]),
    "jenkins":      ("tool", ["jenkins"]),
}

# Index inverse : alias (minuscule) -> skill canonique
ALIAS_VERS_SKILL: dict[str, str] = {
    alias: canonique
    for canonique, (_, aliases) in ONTOLOGIE.items()
    for alias in aliases
}

# Alias trop ambigus pour être cherchés dans le texte libre d'un CV
# ("c", "r", "go", "bi"... apparaissent comme mots normaux). On ne les
# reconnaît QUE dans la section Compétences, où le contexte est sans ambiguïté.
ALIAS_AMBIGUS = {"c", "r", "go", "ml", "bi", "ts", "js"}


def normaliser_skill(brut: str) -> Optional[tuple[str, str]]:
    """'Python 3' -> ('python', 'language'). None si inconnu de l'ontologie.

    1. Nettoyage (minuscules, espaces, numéro de version en fin)
    2. Correspondance exacte dans les alias
    3. Fuzzy matching difflib (tolère les fautes : 'postgress' -> postgresql)
    """
    t = brut.strip().lower()
    t = re.sub(r"\s+", " ", t)
    t = re.sub(r"\s*\d+(\.\d+)*$", "", t)  # "python 3.11" -> "python"
    if not t:
        return None

    if t in ALIAS_VERS_SKILL:
        canonique = ALIAS_VERS_SKILL[t]
        return canonique, ONTOLOGIE[canonique][0]

    # Fuzzy : uniquement sur les alias non ambigus, seuil élevé (évite les
    # faux positifs : on préfère rater un skill qu'en inventer un)
    candidats = [a for a in ALIAS_VERS_SKILL if a not in ALIAS_AMBIGUS]
    proches = get_close_matches(t, candidats, n=1, cutoff=0.85)
    if proches:
        canonique = ALIAS_VERS_SKILL[proches[0]]
        return canonique, ONTOLOGIE[canonique][0]
    return None
