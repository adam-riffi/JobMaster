"""Aleister — Générateur de flux JobMaster.

Wizard guidé : définir le contexte, obtenir des questions de clarification,
puis générer YAML + SQL conformes à la grammaire JobMaster v1.3.
"""

import streamlit as st
from groq import Groq

from aleister.config import GROQ_API_KEY, MODELES_GROQ, FLOW_TYPES, PLATFORMS, LOAD_MODES
from aleister.backend.generator import (
    generer_workflow,
    poser_questions_ia,
    generer_contexte_ia,
    parser_fichiers,
    creer_zip,
    detecter_langage,
)

st.set_page_config(
    page_title="Aleister — Générer un flux",
    page_icon="⚙️",
    layout="wide",
)

st.title("⚙️ Générer un flux")
st.caption("Décris ton besoin, l'IA pose ses questions, puis génère le workflow complet.")

# ── Sidebar config ────────────────────────────────────────────────────────────
st.sidebar.header("Configuration IA")
api_key = st.sidebar.text_input(
    "Clé API Groq",
    value=GROQ_API_KEY,
    type="password",
    help="Récupère ta clé sur console.groq.com/keys",
)
modele = st.sidebar.selectbox("Modèle", MODELES_GROQ)

# ── Session init ──────────────────────────────────────────────────────────────
def _init():
    defaults = {
        "gen_etape": 1,
        "gen_contexte": {},
        "gen_questions": "",
        "gen_reponses": "",
        "gen_resultat": "",
        "gen_fichiers": [],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init()

def _reset():
    for k in list(st.session_state.keys()):
        if k.startswith("gen_"):
            del st.session_state[k]
    _init()

if st.button("Nouveau flux", type="secondary"):
    _reset()
    st.rerun()

st.divider()

# ─────────────────────────────────────────────────────────────────────────────
# ÉTAPE 1 — Contexte
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state["gen_etape"] == 1:
    st.subheader("Étape 1 — Définir le contexte")

    col_left, col_right = st.columns(2)

    with col_left:
        domaine = st.text_input("Domaine métier *", placeholder="Clients, Facturation, Fraude…")
        description = st.text_area(
            "Description du besoin *",
            placeholder="Ex: Rapatriement quotidien des fichiers CDR depuis le SFTP de médiation et chargement en table SOCLE Teradata.",
            height=120,
        )
        dossiers = st.multiselect(
            "Types de flux à générer *",
            FLOW_TYPES,
            default=["Import", "Alimentation"],
        )

    with col_right:
        plateforme = st.selectbox("Plateforme cible *", PLATFORMS)
        source = st.selectbox("Source des données", ["SFTP", "API REST", "Cloud Storage (GCS)", "Fichiers locaux", "(non applicable)"])
        format_fichier = st.selectbox("Format fichier", ["CSV", "JSON", "(non applicable)"])
        separateur = st.text_input("Séparateur CSV", value=";") if format_fichier == "CSV" else ""
        mode_chargement = st.selectbox("Mode de chargement", LOAD_MODES)

    st.subheader("Répertoires (optionnel)")
    c1, c2, c3, c4 = st.columns(4)
    rep_in   = c1.text_input("Entrée",   placeholder=r"C:\data\domain\in")
    rep_work = c2.text_input("Travail",  placeholder=r"C:\data\domain\work")
    rep_arch = c3.text_input("Archive",  placeholder=r"C:\data\domain\archive")
    rep_export = c4.text_input("Export", placeholder=r"C:\data\domain\export")

    instructions = st.text_area(
        "Instructions complémentaires",
        placeholder="Ex: Le fichier est compressé en gzip. La clé primaire est id_client.",
        height=80,
    )

    st.divider()
    col_btn1, col_btn2 = st.columns([1, 3])

    with col_btn1:
        if st.button("Mode Full IA", help="L'IA génère un contexte réaliste complet pour toi."):
            if not api_key:
                st.error("Clé API requise.")
            else:
                with st.spinner("L'IA génère un contexte…"):
                    try:
                        client = Groq(api_key=api_key)
                        ctx = generer_contexte_ia(client, modele)
                        st.session_state["gen_contexte"] = ctx
                        st.session_state["gen_etape"] = 2
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erreur : {e}")

    with col_btn2:
        if st.button("Suivant → Clarification", type="primary", disabled=not (domaine and description and dossiers)):
            st.session_state["gen_contexte"] = {
                "domaine":                    domaine,
                "description":                description,
                "dossiers":                   dossiers,
                "plateforme":                 plateforme,
                "source":                     source if source != "(non applicable)" else "",
                "format_fichier":             format_fichier if format_fichier != "(non applicable)" else "",
                "separateur":                 separateur,
                "mode_chargement":            mode_chargement,
                "rep_in":                     rep_in,
                "rep_work":                   rep_work,
                "rep_arch":                   rep_arch,
                "rep_export":                 rep_export,
                "instructions_supplementaires": instructions,
            }
            st.session_state["gen_etape"] = 2
            st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# ÉTAPE 2 — Clarification IA
# ─────────────────────────────────────────────────────────────────────────────
elif st.session_state["gen_etape"] == 2:
    ctx = st.session_state["gen_contexte"]
    st.subheader("Étape 2 — Clarification IA")

    with st.expander("Contexte collecté", expanded=False):
        st.json(ctx)

    if not st.session_state["gen_questions"]:
        if not api_key:
            st.error("Clé API requise pour la clarification.")
        else:
            with st.spinner("L'IA formule ses questions…"):
                try:
                    client = Groq(api_key=api_key)
                    questions = poser_questions_ia(client, modele, ctx)
                    st.session_state["gen_questions"] = questions
                    st.rerun()
                except Exception as e:
                    st.error(f"Erreur : {e}")
                    st.stop()

    if st.session_state["gen_questions"]:
        st.markdown("**Questions de l'IA :**")
        st.markdown(st.session_state["gen_questions"])
        st.divider()
        reponses = st.text_area(
            "Tes réponses (optionnel — laisse vide pour passer directement à la génération)",
            value=st.session_state["gen_reponses"],
            height=150,
        )
        st.session_state["gen_reponses"] = reponses

        col_back, col_next = st.columns([1, 3])
        with col_back:
            if st.button("← Retour"):
                st.session_state["gen_etape"] = 1
                st.rerun()
        with col_next:
            if st.button("Générer le workflow →", type="primary"):
                if reponses:
                    ctx["instructions_supplementaires"] = (
                        (ctx.get("instructions_supplementaires") or "") +
                        f"\n\nRéponses aux questions de clarification :\n{reponses}"
                    )
                    st.session_state["gen_contexte"] = ctx
                st.session_state["gen_etape"] = 3
                st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# ÉTAPE 3 — Génération
# ─────────────────────────────────────────────────────────────────────────────
elif st.session_state["gen_etape"] == 3:
    ctx = st.session_state["gen_contexte"]
    st.subheader("Étape 3 — Génération du workflow")

    if not st.session_state["gen_resultat"]:
        if not api_key:
            st.error("Clé API requise.")
            st.stop()
        with st.spinner("L'IA génère le workflow complet…"):
            try:
                client = Groq(api_key=api_key)
                resultat = generer_workflow(client, modele, ctx)
                fichiers = parser_fichiers(resultat)
                st.session_state["gen_resultat"] = resultat
                st.session_state["gen_fichiers"] = fichiers
                st.rerun()
            except Exception as e:
                st.error(f"Erreur lors de la génération : {e}")
                st.stop()

    fichiers = st.session_state["gen_fichiers"]
    st.success(f"{len(fichiers)} fichier(s) généré(s).")

    if fichiers:
        zip_data = creer_zip(fichiers)
        st.download_button(
            label="Télécharger le ZIP",
            data=zip_data,
            file_name=f"{ctx.get('domaine', 'workflow')}_jobmaster.zip",
            mime="application/zip",
            type="primary",
        )

    st.divider()

    for f in fichiers:
        lang = detecter_langage(f["chemin"])
        with st.expander(f["chemin"], expanded=False):
            st.code(f["contenu"], language=lang or None)

    col_back, _ = st.columns([1, 3])
    with col_back:
        if st.button("← Recommencer"):
            _reset()
            st.rerun()
