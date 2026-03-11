"""Aleister — Générateur de flux (appel Groq + parsing)."""

import io
import os
import re
import zipfile

from groq import Groq

from aleister.config import DOC_PATH, GROQ_API_KEY
from aleister.backend.prompts import construire_system_prompt, construire_user_prompt


# ── Documentation ─────────────────────────────────────────────────────────────
_DOC_CACHE: str | None = None


def charger_documentation() -> str:
    """Charge le fichier de documentation JobMaster (mise en cache)."""
    global _DOC_CACHE
    if _DOC_CACHE is None:
        if not DOC_PATH.exists():
            raise FileNotFoundError(f"Documentation introuvable : {DOC_PATH}")
        _DOC_CACHE = DOC_PATH.read_text(encoding="utf-8")
    return _DOC_CACHE


# ── Client Groq ───────────────────────────────────────────────────────────────
def get_groq_client(api_key: str = "") -> Groq:
    key = api_key or GROQ_API_KEY
    if not key:
        raise ValueError("GROQ_API_KEY manquant")
    return Groq(api_key=key)


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


# ── Génération ────────────────────────────────────────────────────────────────
def generer_workflow(
    client: Groq,
    modele: str,
    contexte: dict,
) -> str:
    """Génère un workflow complet à partir du contexte collecté."""
    doc = charger_documentation()
    messages = [
        {"role": "system", "content": construire_system_prompt(doc)},
        {"role": "user",   "content": construire_user_prompt(contexte)},
    ]
    return appeler_groq(client, modele, messages, temperature=0.3, max_tokens=8000)


def poser_questions_ia(
    client: Groq,
    modele: str,
    contexte: dict,
) -> str:
    """Demande à l'IA de poser des questions de clarification."""
    doc = charger_documentation()
    system_prompt = (
        "Tu es un expert JobMaster v1.3. On te donne les paramètres partiels d'un workflow. "
        "Analyse-les et pose 3 à 6 questions précises pour clarifier les détails manquants.\n"
        "Concentre-toi sur :\n"
        "- La structure des données si absente (colonnes, types)\n"
        "- Les chemins de fichiers et URIs\n"
        "- Les règles métier (fréquence, purge, masque fichier)\n"
        "- Le mode de chargement (FULL, INSERT, UPSERT, UPDATE)\n"
        "- Les tables de staging et socle\n\n"
        "Réponds UNIQUEMENT avec une liste numérotée de questions. Pas d'introduction, pas de conclusion.\n\n"
        f"DOCUMENTATION OFFICIELLE :\n{doc}"
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user",   "content": f"Voici le contexte partiel :\n\n{construire_user_prompt(contexte)}"},
    ]
    return appeler_groq(client, modele, messages, temperature=0.4, max_tokens=2000)


def generer_contexte_ia(client: Groq, modele: str) -> dict:
    """Mode Full IA : génère un contexte réaliste complet."""
    import json
    import random

    doc = charger_documentation()

    domaines_exemples = [
        "Clients", "Contrats", "Facturation", "Paiements",
        "Consommations CDR", "Roaming", "Fraude", "Recouvrement",
        "Commandes", "Produits", "Marketing", "Ventes",
        "Service Client", "Reporting", "Paie", "Incidents Réseau",
    ]
    domaine_impose    = random.choice(domaines_exemples)
    plateforme_imposee = random.choice(["BQ", "TD"])
    type_impose       = random.choice(["Import+Alimentation", "Alimentation+Export", "Aggregat"])

    system_prompt = (
        "Tu es un expert Data Engineering. Invente un cas d'usage réaliste pour un workflow "
        "JobMaster v1.3 avec le domaine, la plateforme et le type imposés. "
        "Génère un contexte JSON complet avec ces champs :\n\n"
        "- domaine : nom du domaine métier\n"
        "- description : description détaillée du besoin en 2-3 phrases\n"
        '- plateforme : "BQ" ou "TD"\n'
        '- dossiers : liste parmi ["Import", "Alimentation", "Export", "Aggregat"]\n'
        "- source : source des données (SFTP, API REST, Cloud Storage (GCS), Fichiers locaux)\n"
        "- format_fichier : CSV ou JSON\n"
        "- colonnes : liste de 5 à 10 colonnes avec nom, type et nullable (bool)\n"
        "- mode_chargement : FULL, INSERT, UPDATE ou UPSERT\n"
        "- separateur : séparateur CSV (si applicable)\n\n"
        "IMPORTANT : adapte les types de colonnes à la plateforme imposée.\n"
        "  BQ → STRING, INT64, NUMERIC, FLOAT64, BOOL, DATE, TIMESTAMP\n"
        "  TD → VARCHAR(n), INTEGER, DECIMAL(p,s), FLOAT, DATE, TIMESTAMP, BYTEINT\n\n"
        "Réponds UNIQUEMENT avec le JSON, sans introduction ni commentaire.\n\n"
        f"DOCUMENTATION :\n{doc}"
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": (
                f"Domaine : {domaine_impose}\n"
                f"Plateforme : {plateforme_imposee}\n"
                f"Type : {type_impose}\n\n"
                "Génère un contexte de workflow réaliste."
            ),
        },
    ]

    reponse = appeler_groq(client, modele, messages, temperature=0.9, max_tokens=2000)
    cleaned = reponse.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[1]
        cleaned = cleaned.rsplit("```", 1)[0]
    return json.loads(cleaned.strip())


# ── Parsing / export ──────────────────────────────────────────────────────────
def parser_fichiers(reponse: str) -> list[dict]:
    """Extrait les fichiers depuis la réponse de l'IA (format --- FICHIER: ... ---)."""
    pattern = r"---\s*FICHIER:\s*(.+?)\s*---\s*\n(.*?)---\s*FIN FICHIER\s*---"
    return [
        {"chemin": chemin.strip(), "contenu": contenu.strip() + "\n"}
        for chemin, contenu in re.findall(pattern, reponse, re.DOTALL)
    ]


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
