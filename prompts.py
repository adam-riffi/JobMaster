"""
JobMaster — Prompts pour l'IA (Groq)
"""


def construire_system_prompt(documentation: str) -> str:
    """Construit le prompt système pour la génération de workflows."""
    return f"""Tu es un expert JobMaster. Tu génères des workflows YAML et des scripts SQL
conformes à la documentation officielle ci-dessous.

CONTEXTE MÉTIER :
- « Import » = rapatrier la donnée chez nous (SFTP → local, API → fichier, Cloud Storage → disque).
  Un dossier Import ne contient AUCUN INSERT/UPSERT en base.
- « Alimentation » = charger / transformer la donnée en base (INSERT, UPSERT, CREATE VIEW, etc.).
  Dès qu'il y a un INSERT ou un chargement en table, c'est un dossier Alimentation.
- « Export » = extraire la donnée et l'envoyer à l'extérieur (fichier → SFTP/API/Cloud Storage).

RÈGLES ABSOLUES :
- Respecte EXACTEMENT le format YAML de la documentation (indentation 2 espaces, pas d'onglet).
- Utilise UNIQUEMENT les job_id du catalogue officiel (10 jobs).
- Tous les paramètres listés pour un job_id sont OBLIGATOIRES.
- Le préfixe des variables est « £ » (jamais #, jamais $).
- Aère les scripts : ligne vide après la description, après parametres_env, et entre chaque job.
- Le format de id_script est Domaine_Type_Nom (OBLIGATOIRE).
- Tu choisis toi-même les noms des fichiers YAML et SQL de façon cohérente et descriptive.
  Convention : préfixe par le domaine, en français, snake_case.
- Pour installation/ : chaque SQL doit avoir un YAML correspondant avec un job.run.sql.
- La durée dans job.fichier.effacement est en MOIS (pas en minutes).
- job.run.create_view prend Plateforme + Table (PAS de Requete). La vue est auto-générée.
- Les masques (Masque) sont des expressions régulières (regex).

RÈGLES SQL :
- BigQuery (.gql) : utiliser les types BQ (STRING, INT64, NUMERIC, FLOAT64, DATE, TIMESTAMP, BOOL).
- Teradata (.dql) : utiliser les types TD (VARCHAR(n), INTEGER, DECIMAL(p,s), FLOAT, DATE, TIMESTAMP).
- Les variables £ sont substituées dans les SQL (ex. £BQ_TMP.staging_factures).
- Pour charger des données depuis Cloud Storage dans BigQuery :
    • Table externe : CREATE OR REPLACE EXTERNAL TABLE avec OPTIONS (format, uris, skip_leading_rows).
    • Chargement direct : LOAD DATA OVERWRITE ... FROM FILES (...).
    • URI GCS : gs://<bucket>/<chemin>/<pattern>
- Pour Teradata avec NOS :
    • Table externe : CREATE FOREIGN TABLE avec USING (LOCATION, STOREDAS, HEADER).
    • URI S3 : /s3/<bucket>/<chemin>/  |  Azure : /az/<container>/<chemin>/  |  GCS : /gs/<bucket>/<chemin>/
- Chaque SQL commence par un commentaire explicatif en français.
- Un SQL par fichier, atomique (un objet = un fichier).

FORMAT DE RÉPONSE :
Pour chaque fichier à générer, utilise ce format exact :

--- FICHIER: chemin/relatif/du/fichier.yml ---
(contenu du fichier)
--- FIN FICHIER ---

STRUCTURE DES CHEMINS :
Les chemins doivent refléter cette arborescence :
  Domaine/
    Import/
      config/          ← YAML de configuration
      sql/             ← scripts SQL
      installation/    ← sous-dossier d'installation (YAML + SQL)
    Alimentation/
      config/
      sql/
      installation/
    Export/
      config/
      sql/
      installation/
installation/ est TOUJOURS un sous-dossier de Import, Alimentation ou Export (jamais au même niveau).
Génère TOUS les fichiers nécessaires : YAML de config, SQL, et YAML + SQL d'installation.
Ne génère AUCUN texte explicatif en dehors des blocs FICHIER.

DOCUMENTATION OFFICIELLE :
{documentation}"""


def construire_user_prompt(contexte: dict) -> str:
    """Construit le prompt utilisateur à partir du contexte collecté par le wizard."""
    # Dossiers sélectionnés
    dossiers = contexte.get('dossiers', [])
    dossiers_str = ", ".join(dossiers) if dossiers else "à déterminer par l'IA"

    lignes = [
        f"Génère un workflow JobMaster complet avec ces paramètres :\n",
        f"- Domaine : {contexte['domaine']}",
        f"- Dossiers à générer : {dossiers_str}",
        f"- Plateforme : {contexte['plateforme']}",
        f"- Description : {contexte['description']}",
    ]

    # Source
    if contexte.get("source"):
        lignes.append(f"- Source des données : {contexte['source']}")
    if contexte.get("uri_source"):
        lignes.append(f"- URI source : {contexte['uri_source']}")

    # Destination
    if contexte.get("destination"):
        lignes.append(f"- Destination export : {contexte['destination']}")
    if contexte.get("uri_destination"):
        lignes.append(f"- URI destination : {contexte['uri_destination']}")

    # Format
    if contexte.get("format_fichier"):
        lignes.append(f"- Format de fichier : {contexte['format_fichier']}")
    if contexte.get("separateur"):
        lignes.append(f"- Séparateur CSV : {contexte['separateur']}")
    if contexte.get("entete"):
        lignes.append(f"- Fichier avec en-tête : {contexte['entete']}")

    # Tables
    if contexte.get("nom_table_staging"):
        lignes.append(f"- Nom table staging : {contexte['nom_table_staging']}")
    if contexte.get("nom_table_socle"):
        lignes.append(f"- Nom table SOCLE : {contexte['nom_table_socle']}")
    if contexte.get("cle_primaire"):
        lignes.append(f"- Clé primaire (pour MERGE/UPSERT) : {contexte['cle_primaire']}")
    if contexte.get("mode_chargement"):
        lignes.append(f"- Mode de chargement : {contexte['mode_chargement']}")

    # Structure de données
    if contexte.get("colonnes"):
        lignes.append(f"\nStructure des données ({len(contexte['colonnes'])} colonnes) :")
        for col in contexte["colonnes"]:
            nullable = "" if col.get("nullable", True) else " NOT NULL"
            lignes.append(f"  - {col['nom']} ({col['type']}{nullable})")

    # Chemins fichiers
    if contexte.get("rep_in"):
        lignes.append(f"- Répertoire entrée : {contexte['rep_in']}")
    if contexte.get("rep_work"):
        lignes.append(f"- Répertoire travail : {contexte['rep_work']}")
    if contexte.get("rep_arch"):
        lignes.append(f"- Répertoire archive : {contexte['rep_arch']}")
    if contexte.get("rep_export"):
        lignes.append(f"- Répertoire export : {contexte['rep_export']}")

    # Purge
    if contexte.get("duree_purge_archive"):
        lignes.append(f"- Purge archives après : {contexte['duree_purge_archive']} mois")
    if contexte.get("duree_purge_export"):
        lignes.append(f"- Purge exports après : {contexte['duree_purge_export']} mois")

    # Masque fichier
    if contexte.get("masque_fichier"):
        lignes.append(f"- Masque regex des fichiers : {contexte['masque_fichier']}")
    if contexte.get("nom_fichier_export"):
        lignes.append(f"- Nom fichier export : {contexte['nom_fichier_export']}")

    # Instructions complémentaires
    if contexte.get("instructions_supplementaires"):
        lignes.append(f"\nInstructions complémentaires :\n{contexte['instructions_supplementaires']}")

    lignes.append(
        "\nGénère tous les fichiers nécessaires (YAML + SQL + installation) "
        "en respectant strictement la documentation et la structure de données fournie."
    )

    return "\n".join(lignes)
