"""Aleister — Documentation.

Consulte les CDCs existants et génère des fiches de flux / index de domaine.
"""

from pathlib import Path

import streamlit as st

from aleister.config import DOCS_ROOT
from aleister.backend.knowledge_base import build_index
from aleister.backend.doc_builder import flux_to_markdown, domain_index_markdown

st.set_page_config(
    page_title="Aleister — Documentation",
    page_icon="📝",
    layout="wide",
)

st.title("📝 Documentation")
st.caption("Consulte les CDCs et génère des fiches de flux en Markdown.")


# ── Build / cache index ───────────────────────────────────────────────────────
@st.cache_data(ttl=120, show_spinner="Indexation du workspace…")
def _load_index() -> dict:
    return build_index()


idx = _load_index()

tab_cdc, tab_fiches, tab_index = st.tabs(["CDCs existants", "Fiches de flux", "Index domaine"])

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 — CDCs existants
# ─────────────────────────────────────────────────────────────────────────────
with tab_cdc:
    st.subheader("Cahiers des charges (CDCs)")

    if not DOCS_ROOT.exists():
        st.warning(f"Dossier docs introuvable : `{DOCS_ROOT}`")
    else:
        domaines_docs = sorted(d.name for d in DOCS_ROOT.iterdir() if d.is_dir())

        col_dom, col_search = st.columns([2, 3])
        with col_dom:
            sel_dom = st.selectbox("Domaine", ["(tous)"] + domaines_docs, key="cdc_dom")
        with col_search:
            cdc_search = st.text_input("Recherche dans les CDCs", placeholder="upsert, sftp…", key="cdc_search")

        # Collect CDC files
        if sel_dom == "(tous)":
            cdc_files = sorted(DOCS_ROOT.rglob("*_CDC.md"))
        else:
            cdc_files = sorted((DOCS_ROOT / sel_dom).glob("*_CDC.md"))

        if cdc_search:
            kw = cdc_search.lower()
            cdc_files = [p for p in cdc_files if kw in p.stem.lower()]

        st.caption(f"{len(cdc_files)} CDC(s) trouvé(s).")

        if not cdc_files:
            st.info("Aucun CDC ne correspond à la sélection.")
        else:
            selected_cdc = st.selectbox(
                "Sélectionner un CDC",
                cdc_files,
                format_func=lambda p: f"{p.parent.name} / {p.stem}",
                key="cdc_select",
            )
            if selected_cdc:
                content = Path(selected_cdc).read_text(encoding="utf-8")
                st.markdown(content)
                st.download_button(
                    "Télécharger ce CDC",
                    data=content.encode("utf-8"),
                    file_name=Path(selected_cdc).name,
                    mime="text/markdown",
                )

# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 — Fiches de flux
# ─────────────────────────────────────────────────────────────────────────────
with tab_fiches:
    st.subheader("Fiche d'un flux")
    st.caption("Génère une fiche Markdown complète pour un flux indexé.")

    if not idx["flux"]:
        st.warning("Aucun flux indexé.")
    else:
        domaines_flux = ["(tous)"] + idx["domaines"]
        sel_dom_fiche = st.selectbox("Domaine", domaines_flux, key="fiche_dom")

        flux_filtre = idx["flux"] if sel_dom_fiche == "(tous)" else [
            f for f in idx["flux"] if f["domaine"] == sel_dom_fiche
        ]

        sel_flux = st.selectbox(
            "Flux",
            flux_filtre,
            format_func=lambda f: f["id_script"],
            key="fiche_flux",
        )

        if sel_flux:
            fiche = flux_to_markdown(sel_flux)
            st.markdown(fiche)
            st.download_button(
                "Télécharger la fiche",
                data=fiche.encode("utf-8"),
                file_name=f"{sel_flux['id_script']}_fiche.md",
                mime="text/markdown",
            )

# ─────────────────────────────────────────────────────────────────────────────
# TAB 3 — Index domaine
# ─────────────────────────────────────────────────────────────────────────────
with tab_index:
    st.subheader("Index d'un domaine")
    st.caption("Génère l'index complet de tous les flux d'un domaine.")

    if not idx["domaines"]:
        st.warning("Aucun domaine indexé.")
    else:
        sel_dom_idx = st.selectbox("Domaine", idx["domaines"], key="idx_dom")

        if sel_dom_idx:
            index_md = domain_index_markdown(sel_dom_idx, idx)
            st.markdown(index_md)
            st.download_button(
                "Télécharger l'index",
                data=index_md.encode("utf-8"),
                file_name=f"{sel_dom_idx}_index.md",
                mime="text/markdown",
            )
