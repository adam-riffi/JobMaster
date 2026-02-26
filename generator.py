"""
JobMaster — Générateur (appel Groq + parsing)
"""

import io
import os
import re
import zipfile

import streamlit as st
from groq import Groq

from config import DOC_PATH
from prompts import construire_system_prompt, construire_user_prompt


# ---------------------------------------------------------------------------
# Chargement de la documentation
# ---------------------------------------------------------------------------
@st.cache_data
def charger_documentation() -> str:
    """Charge le fichier de documentation JobMaster."""
    if not os.path.exists(DOC_PATH):
        return ""
    with open(DOC_PATH, "r", encoding="utf-8") as f:
        return f.read()


# ---------------------------------------------------------------------------
# Appel Groq
# ---------------------------------------------------------------------------
def appeler_groq(
    client: Groq,
    modele: str,
    messages: list[dict],
    temperature: float = 0.3,
    max_tokens: int = 8000,
) -> str:
    """Appel générique à l'API Groq."""
    completion = client.chat.completions.create(
        messages=messages,
        model=modele,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return completion.choices[0].message.content


def generer_workflow(client: Groq, modele: str, contexte: dict) -> str:
    """Génère un workflow complet à partir du contexte collecté."""
    doc = charger_documentation()
    if not doc:
        raise ValueError("Documentation introuvable (doc.txt)")

    system_prompt = construire_system_prompt(doc)
    user_prompt = construire_user_prompt(contexte)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    return appeler_groq(client, modele, messages, temperature=0.3, max_tokens=8000)


def poser_questions_ia(client: Groq, modele: str, contexte: dict) -> str:
    """Demande à l'IA de poser des questions de clarification."""
    doc = charger_documentation()

    system_prompt = f"""Tu es un expert JobMaster. On te donne les paramètres partiels d'un workflow.
Analyse-les et pose 3 à 6 questions précises pour clarifier les détails manquants.
Concentre-toi sur :
- La structure des données si absente (colonnes, types)
- Les chemins de fichiers et URIs
- Les règles métier (fréquence, purge, masque fichier)
- Le mode de chargement (FULL, INSERT, UPSERT, UPDATE)
- Les tables de staging et socle

Réponds UNIQUEMENT avec une liste numérotée de questions. Pas d'introduction, pas de conclusion.

DOCUMENTATION OFFICIELLE :
{doc}"""

    user_prompt = construire_user_prompt(contexte)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Voici le contexte partiel :\n\n{user_prompt}"},
    ]

    return appeler_groq(client, modele, messages, temperature=0.4, max_tokens=2000)


def generer_contexte_ia(client: Groq, modele: str) -> dict:
    """Mode Full IA : génère un contexte réaliste complet pour la démo."""
    import json
    import random

    doc = charger_documentation()

    # Tirer un domaine au hasard pour forcer la variété
    domaines_exemples = [
        "Clients", "Stocks", "Commandes", "RH (Ressources Humaines)",
        "Logistique", "Fournisseurs", "Produits", "Contrats",
        "Sinistres (Assurance)", "Transactions bancaires", "Abonnements",
        "Campagnes marketing", "Tickets SAV", "Véhicules (Flotte)",
        "Patients (Santé)", "Réservations", "Inventaire", "Paie",
        "Livraisons", "Données IoT capteurs",
    ]
    domaine_impose = random.choice(domaines_exemples)

    # Tirer une plateforme au hasard
    plateforme_imposee = random.choice(["BQ", "TD"])

    system_prompt = (
        "Tu es un expert Data Engineering. Invente un cas d'usage réaliste pour un workflow "
        "JobMaster avec le domaine ET la plateforme imposés ci-dessous. Génère un contexte JSON complet avec ces champs :\n\n"
        "- domaine : nom du domaine métier (UTILISE le domaine imposé)\n"
        "- description : description détaillée du besoin en 2-3 phrases\n"
        '- plateforme : UTILISE la plateforme imposée ("BQ" ou "TD")\n'
        '- dossiers : liste parmi ["Import", "Alimentation", "Export"] (souvent Import + Alimentation)\n'
        "- source : source des données (SFTP, API REST, Cloud Storage (GCS), Fichiers locaux)\n"
        "- format_fichier : CSV ou JSON\n"
        "- colonnes : liste de 5 à 10 colonnes avec nom, type (types BigQuery si BQ, Teradata si TD) et nullable (bool)\n"
        "- mode_chargement : FULL, INSERT, UPDATE ou UPSERT\n"
        "- separateur : séparateur CSV (si applicable)\n\n"
        "IMPORTANT : adapte les types de colonnes à la plateforme imposée.\n"
        "  BQ → STRING, INT64, NUMERIC, FLOAT64, BOOL, DATE, TIMESTAMP\n"
        "  TD → VARCHAR(n), INTEGER, DECIMAL(p,s), FLOAT, DATE, TIMESTAMP, BYTEINT\n\n"
        "Réponds UNIQUEMENT avec le JSON, sans introduction ni commentaire. Le JSON doit être valide.\n\n"
        "DOCUMENTATION :\n" + doc
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Domaine imposé : {domaine_impose}\nPlateforme imposée : {plateforme_imposee}\n\nGénère un contexte de workflow réaliste."},
    ]

    reponse = appeler_groq(client, modele, messages, temperature=0.9, max_tokens=2000)

    # Extraire le JSON de la réponse
    cleaned = reponse.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[1]
        cleaned = cleaned.rsplit("```", 1)[0]
    return json.loads(cleaned.strip())


# ---------------------------------------------------------------------------
# Parsing de la réponse
# ---------------------------------------------------------------------------
def parser_fichiers(reponse: str) -> list[dict]:
    """Extrait les fichiers depuis la réponse de l'IA (format --- FICHIER: ... ---)."""
    fichiers = []
    pattern = r"---\s*FICHIER:\s*(.+?)\s*---\s*\n(.*?)---\s*FIN FICHIER\s*---"
    matches = re.findall(pattern, reponse, re.DOTALL)

    for chemin, contenu in matches:
        chemin = chemin.strip()
        contenu = contenu.strip() + "\n"
        fichiers.append({"chemin": chemin, "contenu": contenu})

    return fichiers


def creer_zip(fichiers: list[dict]) -> bytes:
    """Crée un ZIP en mémoire avec tous les fichiers générés."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in fichiers:
            zf.writestr(f["chemin"], f["contenu"])
    buffer.seek(0)
    return buffer.read()


def detecter_langage(chemin: str) -> str:
    """Détecte le langage pour la coloration syntaxique."""
    if chemin.endswith((".yml", ".yaml")):
        return "yaml"
    if chemin.endswith((".gql", ".dql", ".sql")):
        return "sql"
    return ""
