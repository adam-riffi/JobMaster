"""
JobMaster — Composants UI Streamlit (wizard multi-étapes)
"""

import os
import streamlit as st

from config import (
    DESTINATIONS_EXPORT,
    DOSSIERS_WORKFLOW,
    FORMATS_FICHIERS,
    MODELES_GROQ,
    MODES_CHARGEMENT,
    PLATEFORMES,
    SOURCES_DONNEES,
    TYPES_COLONNES_BQ,
    TYPES_COLONNES_TD,
)
from generator import charger_documentation, detecter_langage


# ---------------------------------------------------------------------------
# Initialisation session state
# ---------------------------------------------------------------------------
def init_session():
    """Initialise les variables de session si absentes."""
    valeurs_defaut = {
        "etape": 1,
        "colonnes": [],
        "questions_ia": "",
        "reponses_ia": "",
        "fichiers_generes": [],
        "reponse_brute": "",
        "contexte": {},
        "mode_full_ia": False,
    }
    for cle, valeur in valeurs_defaut.items():
        if cle not in st.session_state:
            st.session_state[cle] = valeur


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
def afficher_sidebar() -> tuple[str, str]:
    """Affiche la sidebar de configuration. Retourne (api_key, modele)."""
    with st.sidebar:
        st.header("🔑 Configuration")

        api_key = st.text_input(
            "Clé API Groq",
            type="password",
            value=os.getenv("GROQ_API_KEY", ""),
            help="https://console.groq.com/keys",
        )

        modele = st.selectbox("Modèle", MODELES_GROQ, index=0)

        st.divider()
        st.header("📖 Documentation")
        doc = charger_documentation()
        if doc:
            st.success(f"Chargée ({len(doc.splitlines())} lignes)")
        else:
            st.error("Introuvable (doc.txt)")

        st.divider()

        # Indicateur d'étape
        etapes = [
            "1. Paramètres de base",
            "2. Structure des données",
            "3. Détails techniques",
            "4. Questions de l'IA",
            "5. Génération",
        ]
        st.header("📍 Progression")
        for i, e in enumerate(etapes, 1):
            if i < st.session_state["etape"]:
                st.markdown(f"✅ {e}")
            elif i == st.session_state["etape"]:
                st.markdown(f"▶️ **{e}**")
            else:
                st.markdown(f"⬜ {e}")

        st.divider()
        if st.button("🔄 Recommencer", use_container_width=True):
            for cle in ["etape", "colonnes", "questions_ia", "reponses_ia",
                        "fichiers_generes", "reponse_brute", "contexte", "mode_full_ia"]:
                if cle in st.session_state:
                    del st.session_state[cle]
            st.rerun()

        st.caption("JobMaster v1.2")

    return api_key, modele


# ---------------------------------------------------------------------------
# Étape 1 : Paramètres de base
# ---------------------------------------------------------------------------
def afficher_etape_1(api_key: str, modele: str):
    """Domaine, dossiers, plateforme, description + mode Full IA."""
    st.header("📝 Étape 1 — Paramètres de base")

    # --- Mode Full IA ---
    st.markdown("##### 🤖 Mode démonstration")
    if st.button("🎲 Tout générer par l'IA (demo)", use_container_width=True,
                 help="L'IA invente un cas d'usage réaliste avec colonnes, types, etc."):
        if not api_key:
            st.error("Renseignez votre clé API Groq dans la sidebar.")
        else:
            from generator import generer_contexte_ia
            from groq import Groq
            with st.spinner("L'IA invente un contexte réaliste..."):
                try:
                    client = Groq(api_key=api_key)
                    ctx_ia = generer_contexte_ia(client, modele)
                    # Injecter dans la session
                    st.session_state["contexte"] = ctx_ia
                    st.session_state["colonnes"] = ctx_ia.get("colonnes", [])
                    st.session_state["mode_full_ia"] = True
                    st.session_state["etape"] = 5  # direct en génération
                    st.rerun()
                except Exception as e:
                    st.error(f"Erreur : {e}")

    st.divider()

    ctx = st.session_state["contexte"]

    ctx["domaine"] = st.text_input(
        "Domaine métier *",
        value=ctx.get("domaine", ""),
        placeholder="Ex : Clients, Facturation, Salesforce...",
    )

    # Dossiers à générer (checkboxes)
    st.markdown("**Dossiers à générer** *")
    dossiers_selectionnes = ctx.get("dossiers", [])
    dossiers_maj = []
    for nom, desc in DOSSIERS_WORKFLOW.items():
        checked = st.checkbox(f"**{nom}** — {desc}", value=(nom in dossiers_selectionnes), key=f"dossier_{nom}")
        if checked:
            dossiers_maj.append(nom)
    ctx["dossiers"] = dossiers_maj

    ctx["plateforme"] = st.selectbox(
        "Plateforme cible *",
        PLATEFORMES,
        index=PLATEFORMES.index(ctx["plateforme"]) if ctx.get("plateforme") in PLATEFORMES else 0,
    )

    ctx["description"] = st.text_area(
        "Description du besoin *",
        value=ctx.get("description", ""),
        height=120,
        placeholder="Décrivez votre workflow en langage naturel...",
    )

    # Options conditionnelles selon les dossiers
    afficher_import = "Import" in dossiers_maj
    afficher_export = "Export" in dossiers_maj

    if afficher_import:
        ctx["source"] = st.selectbox("Source des données", SOURCES_DONNEES,
                                     index=SOURCES_DONNEES.index(ctx["source"]) if ctx.get("source") in SOURCES_DONNEES else 0)
        ctx["format_fichier"] = st.selectbox("Format du fichier", FORMATS_FICHIERS,
                                             index=FORMATS_FICHIERS.index(ctx["format_fichier"]) if ctx.get("format_fichier") in FORMATS_FICHIERS else 0)

    if afficher_export:
        ctx["destination"] = st.selectbox("Destination de l'export", DESTINATIONS_EXPORT,
                                          index=DESTINATIONS_EXPORT.index(ctx["destination"]) if ctx.get("destination") in DESTINATIONS_EXPORT else 0)

    st.session_state["contexte"] = ctx

    # Validation
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("Suivant ➡️", type="primary", use_container_width=True):
            if not ctx.get("domaine") or not ctx.get("description"):
                st.error("Domaine et description sont obligatoires.")
            elif not ctx.get("dossiers"):
                st.error("Sélectionnez au moins un dossier.")
            else:
                st.session_state["etape"] = 2
                st.rerun()


# ---------------------------------------------------------------------------
# Étape 2 : Structure des données (éditeur de colonnes)
# ---------------------------------------------------------------------------
def afficher_etape_2():
    """Éditeur interactif de colonnes."""
    st.header("📊 Étape 2 — Structure des données")
    st.caption("Définissez les colonnes de vos tables. L'IA les utilisera pour le SQL.")

    ctx = st.session_state["contexte"]
    plateforme = ctx.get("plateforme", "BQ")
    types_colonnes = TYPES_COLONNES_BQ if plateforme == "BQ" else TYPES_COLONNES_TD

    # Initialiser les colonnes depuis la session
    colonnes = st.session_state["colonnes"]

    # Bouton ajout
    col_add, col_bulk = st.columns(2)
    with col_add:
        if st.button("➕ Ajouter une colonne", use_container_width=True):
            colonnes.append({"nom": "", "type": types_colonnes[0], "nullable": True})
            st.session_state["colonnes"] = colonnes
            st.rerun()
    with col_bulk:
        if st.button("📋 Ajouter par lot (CSV)", use_container_width=True):
            st.session_state["_bulk_mode"] = True
            st.rerun()

    # Mode ajout par lot
    if st.session_state.get("_bulk_mode"):
        st.info("Collez vos colonnes au format : `nom,type` (une par ligne). Le type est optionnel (STRING par défaut).")
        bulk_input = st.text_area("Colonnes en lot", height=120,
                                  placeholder="id,INT64\nnom\ndate_creation,DATE\nmontant,NUMERIC")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("✅ Importer", use_container_width=True):
                for line in bulk_input.strip().splitlines():
                    parts = [p.strip() for p in line.split(",")]
                    nom = parts[0] if parts else ""
                    typ = parts[1] if len(parts) > 1 and parts[1] in types_colonnes else types_colonnes[0]
                    if nom:
                        colonnes.append({"nom": nom, "type": typ, "nullable": True})
                st.session_state["colonnes"] = colonnes
                st.session_state["_bulk_mode"] = False
                st.rerun()
        with c2:
            if st.button("❌ Annuler", use_container_width=True):
                st.session_state["_bulk_mode"] = False
                st.rerun()

    # Affichage des colonnes
    if colonnes:
        st.divider()
        indices_a_supprimer = []

        for i, col in enumerate(colonnes):
            c1, c2, c3, c4 = st.columns([3, 2, 1, 1])
            with c1:
                colonnes[i]["nom"] = st.text_input(
                    "Nom", value=col["nom"], key=f"col_nom_{i}",
                    placeholder="nom_colonne", label_visibility="collapsed"
                )
            with c2:
                idx_type = types_colonnes.index(col["type"]) if col["type"] in types_colonnes else 0
                colonnes[i]["type"] = st.selectbox(
                    "Type", types_colonnes, index=idx_type,
                    key=f"col_type_{i}", label_visibility="collapsed"
                )
            with c3:
                colonnes[i]["nullable"] = st.checkbox(
                    "NULL", value=col.get("nullable", True), key=f"col_null_{i}"
                )
            with c4:
                if st.button("🗑️", key=f"col_del_{i}"):
                    indices_a_supprimer.append(i)

        # Supprimer les colonnes marquées
        if indices_a_supprimer:
            st.session_state["colonnes"] = [c for j, c in enumerate(colonnes) if j not in indices_a_supprimer]
            st.rerun()

        st.session_state["colonnes"] = colonnes
    else:
        st.info("Aucune colonne définie. L'IA déduira la structure de votre description.")

    # Navigation
    st.divider()
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("⬅️ Retour", use_container_width=True):
            st.session_state["etape"] = 1
            st.rerun()
    with col3:
        if st.button("Suivant ➡️", type="primary", use_container_width=True):
            # Valider les noms de colonnes non vides
            colonnes_valides = [c for c in st.session_state["colonnes"] if c["nom"].strip()]
            st.session_state["colonnes"] = colonnes_valides
            st.session_state["contexte"]["colonnes"] = colonnes_valides
            st.session_state["etape"] = 3
            st.rerun()


# ---------------------------------------------------------------------------
# Étape 3 : Détails techniques
# ---------------------------------------------------------------------------
def afficher_etape_3():
    """Chemins, masques, tables, mode de chargement."""
    st.header("⚙️ Étape 3 — Détails techniques")
    st.caption("Optionnel — l'IA proposera des valeurs par défaut si vous laissez vide.")

    ctx = st.session_state["contexte"]
    dossiers = ctx.get("dossiers", [])

    afficher_import = "Import" in dossiers
    afficher_alim = "Alimentation" in dossiers
    afficher_export = "Export" in dossiers

    if afficher_import:
        st.subheader("📥 Import")
        c1, c2 = st.columns(2)
        with c1:
            ctx["masque_fichier"] = st.text_input(
                "Masque fichier (regex)", value=ctx.get("masque_fichier", ""),
                placeholder=r"Ex : ^factures_\d{8}\.csv$")
            ctx["rep_in"] = st.text_input(
                "Répertoire entrée", value=ctx.get("rep_in", ""),
                placeholder=r"£REP_IN")
        with c2:
            ctx["rep_work"] = st.text_input(
                "Répertoire travail", value=ctx.get("rep_work", ""),
                placeholder=r"£REP_WORK")
            ctx["rep_arch"] = st.text_input(
                "Répertoire archive", value=ctx.get("rep_arch", ""),
                placeholder=r"£REP_ARCH")

        ctx["separateur"] = st.text_input(
            "Séparateur CSV", value=ctx.get("separateur", ""),
            placeholder="Ex : ;  ou  ,  ou  |")
        ctx["entete"] = st.selectbox(
            "Fichier avec en-tête ?", ["Oui", "Non"],
            index=0 if ctx.get("entete", "Oui") == "Oui" else 1)

        if ctx.get("source") == "Cloud Storage (GCS)":
            ctx["uri_source"] = st.text_input(
                "URI Cloud Storage source",
                value=ctx.get("uri_source", ""),
                placeholder="gs://mon-bucket/dossier/fichier_*.csv")

        ctx["nom_table_staging"] = st.text_input(
            "Nom table staging", value=ctx.get("nom_table_staging", ""),
            placeholder=f"Ex : £BQ_TMP.staging_{ctx.get('domaine', 'xxx').lower()}")

    if afficher_alim:
        st.subheader("🔄 Alimentation")
        c1, c2 = st.columns(2)
        with c1:
            ctx["nom_table_socle"] = st.text_input(
                "Nom table SOCLE", value=ctx.get("nom_table_socle", ""),
                placeholder=f"Ex : £BQ_DWH.{ctx.get('domaine', 'xxx').lower()}")
            ctx["mode_chargement"] = st.selectbox(
                "Mode de chargement", MODES_CHARGEMENT,
                index=MODES_CHARGEMENT.index(ctx["mode_chargement"]) if ctx.get("mode_chargement") in MODES_CHARGEMENT else 0)
        with c2:
            if ctx.get("mode_chargement") in ("UPSERT", "UPDATE"):
                ctx["cle_primaire"] = st.text_input(
                    "Clé primaire (pour MERGE)", value=ctx.get("cle_primaire", ""),
                    placeholder="Ex : id_facture")

    if afficher_export:
        st.subheader("📤 Export")
        c1, c2 = st.columns(2)
        with c1:
            ctx["rep_export"] = st.text_input(
                "Répertoire export", value=ctx.get("rep_export", ""),
                placeholder=r"£REP_EXPORT")
            ctx["nom_fichier_export"] = st.text_input(
                "Nom fichier export", value=ctx.get("nom_fichier_export", ""),
                placeholder=f"Ex : export_{ctx.get('domaine', 'xxx').lower()}_AAAAMMJJ.csv")
        with c2:
            if ctx.get("destination") == "Cloud Storage (GCS)":
                ctx["uri_destination"] = st.text_input(
                    "URI Cloud Storage destination",
                    value=ctx.get("uri_destination", ""),
                    placeholder="gs://mon-bucket/exports/")

    st.subheader("🗑️ Purge")
    c1, c2 = st.columns(2)
    with c1:
        ctx["duree_purge_archive"] = st.number_input(
            "Purge archives (mois)", min_value=0, max_value=120,
            value=ctx.get("duree_purge_archive", 6))
    with c2:
        ctx["duree_purge_export"] = st.number_input(
            "Purge exports (mois)", min_value=0, max_value=120,
            value=ctx.get("duree_purge_export", 3))

    ctx["instructions_supplementaires"] = st.text_area(
        "Instructions supplémentaires pour l'IA",
        value=ctx.get("instructions_supplementaires", ""),
        height=80,
        placeholder="Ajoutez des précisions, règles métier, ou contraintes particulières...")

    st.session_state["contexte"] = ctx

    # Navigation
    st.divider()
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("⬅️ Retour", use_container_width=True):
            st.session_state["etape"] = 2
            st.rerun()
    with col3:
        if st.button("Suivant ➡️", type="primary", use_container_width=True):
            st.session_state["etape"] = 4
            st.rerun()


# ---------------------------------------------------------------------------
# Étape 4 : Questions de l'IA
# ---------------------------------------------------------------------------
def afficher_etape_4(api_key: str, modele: str):
    """L'IA pose des questions de clarification."""
    from generator import poser_questions_ia
    from groq import Groq

    st.header("🤖 Étape 4 — Questions de l'IA")
    st.caption("L'IA analyse votre contexte et pose des questions pour affiner la génération.")

    ctx = st.session_state["contexte"]

    # Générer les questions si pas encore fait
    if not st.session_state["questions_ia"]:
        if not api_key:
            st.error("Renseignez votre clé API Groq dans la sidebar.")
            return

        with st.spinner("L'IA analyse votre contexte..."):
            try:
                client = Groq(api_key=api_key)
                questions = poser_questions_ia(client, modele, ctx)
                st.session_state["questions_ia"] = questions
            except Exception as e:
                st.error(f"Erreur API Groq : {e}")
                return

    # Afficher les questions
    st.markdown("### Questions de l'IA :")
    st.markdown(st.session_state["questions_ia"])

    st.divider()
    st.markdown("### Vos réponses :")
    st.session_state["reponses_ia"] = st.text_area(
        "Répondez aux questions ci-dessus",
        value=st.session_state["reponses_ia"],
        height=200,
        placeholder="1. ...\n2. ...\n3. ...",
        label_visibility="collapsed",
    )

    # Navigation
    st.divider()
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("⬅️ Retour", use_container_width=True):
            st.session_state["etape"] = 3
            st.rerun()
    with col2:
        if st.button("🔄 Reposer les questions", use_container_width=True):
            st.session_state["questions_ia"] = ""
            st.rerun()
    with col3:
        skip = not st.session_state["reponses_ia"].strip()
        label = "Générer ➡️ (sans répondre)" if skip else "Générer ➡️"
        if st.button(label, type="primary", use_container_width=True):
            # Ajouter les réponses au contexte
            if st.session_state["reponses_ia"].strip():
                ctx["instructions_supplementaires"] = (
                    ctx.get("instructions_supplementaires", "")
                    + "\n\nRéponses aux questions de clarification :\n"
                    + st.session_state["reponses_ia"]
                )
                st.session_state["contexte"] = ctx
            st.session_state["etape"] = 5
            st.rerun()


# ---------------------------------------------------------------------------
# Arborescence de fichiers (vue explorateur)
# ---------------------------------------------------------------------------
def _construire_arbre(fichiers: list[dict]) -> dict:
    """Construit un arbre imbriqué à partir des chemins de fichiers.

    Retourne un dict récursif :
      { "sous_dossier": { ... }, "_fichiers": [list of file dicts] }
    """
    arbre: dict = {}
    for f in fichiers:
        parts = f["chemin"].replace("\\", "/").strip("/").split("/")
        noeud = arbre
        for segment in parts[:-1]:
            noeud = noeud.setdefault(segment, {})
        noeud.setdefault("_fichiers", []).append(f)
    return arbre


def _icone_dossier(nom: str) -> str:
    nom_lower = nom.lower()
    if "install" in nom_lower:
        return "🔧"
    if "sql" in nom_lower:
        return "🗄️"
    if "config" in nom_lower:
        return "⚙️"
    if "import" in nom_lower:
        return "📥"
    if "alimentation" in nom_lower:
        return "🔄"
    if "export" in nom_lower:
        return "📤"
    return "📁"


def _afficher_noeud(nom: str, noeud: dict, profondeur: int = 0):
    """Affiche récursivement un nœud de l'arbre dans des expanders imbriqués."""
    # Récupérer sous-dossiers et fichiers à ce niveau
    sous_dossiers = {k: v for k, v in sorted(noeud.items()) if k != "_fichiers"}
    fichiers_ici = noeud.get("_fichiers", [])

    icone = _icone_dossier(nom)
    # Comptage total de fichiers sous ce noeud
    nb_total = _compter_fichiers(noeud)
    label = f"{icone} {nom}/  ({nb_total} fichier{'s' if nb_total > 1 else ''})"

    expanded = profondeur < 1  # déplier le premier niveau seulement
    with st.expander(label, expanded=expanded):
        # Afficher les fichiers à ce niveau
        for f in fichiers_ici:
            nom_fichier = f["chemin"].replace("\\", "/").split("/")[-1]
            lang = detecter_langage(f["chemin"])
            st.markdown(f"**📄 {nom_fichier}**")
            st.code(f["contenu"], language=lang)

            cle_dl = f"dl_{f['chemin'].replace('/', '_').replace('.', '_').replace(' ', '_')}"
            st.download_button(
                label=f"Télécharger {nom_fichier}",
                data=f["contenu"],
                file_name=nom_fichier,
                key=cle_dl,
            )

        # Afficher les sous-dossiers récursivement
        for sous_nom, sous_noeud in sous_dossiers.items():
            _afficher_noeud(sous_nom, sous_noeud, profondeur + 1)


def _compter_fichiers(noeud: dict) -> int:
    """Compte récursivement le nombre de fichiers dans un nœud."""
    total = len(noeud.get("_fichiers", []))
    for k, v in noeud.items():
        if k != "_fichiers" and isinstance(v, dict):
            total += _compter_fichiers(v)
    return total


def _afficher_arborescence(fichiers: list[dict]):
    """Point d'entrée : affiche l'arbre complet des fichiers générés."""
    arbre = _construire_arbre(fichiers)

    # Si un seul dossier racine (ex: "Facturation"), on l'affiche directement
    cles_racine = [k for k in arbre if k != "_fichiers"]
    fichiers_racine = arbre.get("_fichiers", [])

    # Fichiers à la racine (rare)
    for f in fichiers_racine:
        nom_fichier = f["chemin"].replace("\\", "/").split("/")[-1]
        lang = detecter_langage(f["chemin"])
        st.markdown(f"**📄 {nom_fichier}**")
        st.code(f["contenu"], language=lang)

    # Sous-dossiers
    for nom in sorted(cles_racine):
        _afficher_noeud(nom, arbre[nom], profondeur=0)


# ---------------------------------------------------------------------------
# Étape 5 : Génération + résultats
# ---------------------------------------------------------------------------
def afficher_etape_5(api_key: str, modele: str):
    """Génération et affichage des résultats avec vue par dossier."""
    from generator import creer_zip, generer_workflow, parser_fichiers
    from groq import Groq

    st.header("📂 Étape 5 — Résultat")

    ctx = st.session_state["contexte"]

    # Lancer la génération si pas encore fait
    if not st.session_state["fichiers_generes"]:
        if not api_key:
            st.error("Renseignez votre clé API Groq dans la sidebar.")
            return

        with st.spinner("Génération du workflow en cours..."):
            try:
                client = Groq(api_key=api_key)
                reponse = generer_workflow(client, modele, ctx)
                fichiers = parser_fichiers(reponse)
                st.session_state["reponse_brute"] = reponse
                st.session_state["fichiers_generes"] = fichiers
            except Exception as e:
                st.error(f"Erreur API Groq : {e}")
                return

    fichiers = st.session_state["fichiers_generes"]

    if fichiers:
        st.success(f"✅ {len(fichiers)} fichier(s) généré(s)")

        # Bouton ZIP
        zip_bytes = creer_zip(fichiers)
        domaine = ctx.get("domaine", "workflow")
        st.download_button(
            label="📦 Télécharger le ZIP",
            data=zip_bytes,
            file_name=f"{domaine}_jobmaster.zip",
            mime="application/zip",
            use_container_width=True,
        )

        # --- Vue arborescente ---
        _afficher_arborescence(fichiers)

    else:
        st.warning("Aucun fichier détecté dans la réponse.")
        with st.expander("Réponse brute de l'IA"):
            st.code(st.session_state.get("reponse_brute", ""), language="text")

    # Navigation
    st.divider()
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("⬅️ Retour", use_container_width=True):
            st.session_state["etape"] = 4
            st.rerun()
    with col2:
        if st.button("🔄 Régénérer", use_container_width=True):
            st.session_state["fichiers_generes"] = []
            st.session_state["reponse_brute"] = ""
            st.rerun()


# ---------------------------------------------------------------------------
# Récapitulatif (affiché en bas de chaque étape)
# ---------------------------------------------------------------------------
def afficher_recap():
    """Affiche un résumé compact du contexte actuel."""
    ctx = st.session_state["contexte"]
    if not ctx.get("domaine"):
        return

    with st.sidebar:
        st.divider()
        st.header("📋 Récapitulatif")
        if ctx.get("domaine"):
            st.markdown(f"**Domaine** : {ctx['domaine']}")
        if ctx.get("plateforme"):
            st.markdown(f"**Plateforme** : {ctx['plateforme']}")
        if ctx.get("dossiers"):
            st.markdown(f"**Dossiers** : {', '.join(ctx['dossiers'])}")
        nb_cols = len(st.session_state.get("colonnes", []))
        if nb_cols:
            st.markdown(f"**Colonnes** : {nb_cols}")
