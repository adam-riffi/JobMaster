"""
JobMaster — Configuration centrale
"""

import os

# Chemin de la documentation
DOC_PATH = os.path.join(os.path.dirname(__file__), "doc.txt")

# Dossiers de workflow (l'utilisateur coche ceux qui s'appliquent)
DOSSIERS_WORKFLOW = {
    "Import": "Rapatrier la donnée chez nous (SFTP, API, Cloud Storage → fichier local)",
    "Alimentation": "Charger / transformer la donnée en base (INSERT, UPSERT, vues…)",
    "Export": "Extraire et envoyer la donnée vers l'extérieur (SFTP, API, Cloud Storage)",
}

# Plateformes supportées
PLATEFORMES = ["BQ", "TD"]

# Sources de données
SOURCES_DONNEES = ["SFTP", "API REST", "Cloud Storage (GCS)", "Fichiers locaux"]

# Destinations d'export
DESTINATIONS_EXPORT = ["SFTP", "API REST", "Cloud Storage (GCS)"]

# Formats de fichiers
FORMATS_FICHIERS = ["CSV", "JSON"]

# Types de colonnes par plateforme
TYPES_COLONNES_BQ = [
    "STRING",
    "INT64",
    "NUMERIC",
    "FLOAT64",
    "BOOL",
    "DATE",
    "TIMESTAMP",
    "BYTES",
]

TYPES_COLONNES_TD = [
    "VARCHAR(255)",
    "INTEGER",
    "BIGINT",
    "DECIMAL(15,2)",
    "FLOAT",
    "DATE",
    "TIMESTAMP",
    "BYTEINT",
    "BYTE(100)",
]

# Modèles Groq
MODELES_GROQ = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "gemma2-9b-it",
    "mixtral-8x7b-32768",
]

# Modes de chargement
MODES_CHARGEMENT = ["FULL", "INSERT", "UPDATE", "UPSERT"]
