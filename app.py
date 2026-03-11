"""Aleister — Page d'accueil.

Hub de navigation vers les 4 modules opérationnels.
"""

import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Aleister — Intelligence JobMaster",
    page_icon="⚡",
    layout="wide",
)


@st.cache_data(ttl=60)
def _quick_stats() -> tuple[int, int, int, int]:
    root = Path(os.getenv("WORKSPACE_ROOT", "workspaces"))
    docs = Path(os.getenv("DOCS_ROOT", "docs"))
    if not root.exists():
        return 0, 0, 0, 0
    domains = sum(1 for d in root.iterdir() if d.is_dir())
    yamls   = sum(1 for _ in root.rglob("*.yml"))
    sqls    = sum(1 for _ in root.rglob("*.gql")) + sum(1 for _ in root.rglob("*.dql"))
    cdcs    = sum(1 for _ in docs.rglob("*.md")) if docs.exists() else 0
    return domains, yamls, sqls, cdcs


# ── Header ────────────────────────────────────────────────────────────────────
st.title("⚡ Aleister")
st.caption(
    "Intelligence opérationnelle pour les flux **JobMaster** — "
    "Télécom Data Engineering"
)
st.divider()

# ── Stats ─────────────────────────────────────────────────────────────────────
nb_domains, nb_yaml, nb_sql, nb_cdc = _quick_stats()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Domaines", nb_domains)
c2.metric("Flux (YAML)", nb_yaml)
c3.metric("Scripts SQL", nb_sql)
c4.metric("CDCs", nb_cdc)

st.divider()

# ── Navigation tiles ──────────────────────────────────────────────────────────
st.subheader("Modules")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.info(
        "**Base de connaissances**\n\n"
        "Explore et filtre les flux existants par domaine, type ou plateforme. "
        "Visualise les dépendances transverses.",
        icon="📚",
    )
    if st.button("Ouvrir →", key="btn_kb", use_container_width=True):
        st.switch_page("pages/01_Knowledge_Base.py")

with col2:
    st.info(
        "**Analyse d'impact**\n\n"
        "Identifie tous les flux affectés par l'évolution d'une table, "
        "y compris les flux transverses cross-domaine.",
        icon="🔍",
    )
    if st.button("Ouvrir →", key="btn_impact", use_container_width=True):
        st.switch_page("pages/02_Impact_Analysis.py")

with col3:
    st.info(
        "**Générer un flux**\n\n"
        "Crée un nouveau flux JobMaster à partir d'un CDC ou d'une description "
        "libre. Génère YAML + SQL prêts à l'emploi.",
        icon="⚙️",
    )
    if st.button("Ouvrir →", key="btn_gen", use_container_width=True):
        st.switch_page("pages/03_Generate_Flow.py")

with col4:
    st.info(
        "**Documentation**\n\n"
        "Génère les fiches de flux et l'index de domaine en Markdown. "
        "Consulte les CDCs existants.",
        icon="📝",
    )
    if st.button("Ouvrir →", key="btn_doc", use_container_width=True):
        st.switch_page("pages/04_Documentation.py")

st.divider()

# ── Footer ────────────────────────────────────────────────────────────────────
workspace_root = os.getenv("WORKSPACE_ROOT", "workspaces")
docs_root      = os.getenv("DOCS_ROOT", "docs")
st.caption(
    f"Workspace : `{workspace_root}` — "
    f"Docs : `{docs_root}` — "
    f"Grammaire : `jobmaster/doc.txt`"
)
