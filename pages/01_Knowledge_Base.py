"""Aleister — Base de connaissances.

Explore les flux JobMaster existants : filtre par domaine, type, plateforme.
Affiche les dépendances transverses et le contenu des fichiers.
"""

from pathlib import Path

import streamlit as st

from aleister.backend.knowledge_base import build_index

st.set_page_config(
    page_title="Aleister — Base de connaissances",
    page_icon="📚",
    layout="wide",
)

st.title("📚 Base de connaissances")
st.caption("Exploration des flux JobMaster indexés dans le workspace.")

# ── Build / cache index ───────────────────────────────────────────────────────
@st.cache_data(ttl=120, show_spinner="Indexation du workspace…")
def _load_index() -> dict:
    return build_index()


with st.spinner("Chargement de l'index…"):
    idx = _load_index()

if not idx["flux"]:
    st.warning("Aucun flux trouvé dans le workspace. Vérifiez WORKSPACE_ROOT dans votre .env.")
    st.stop()

# ── Sidebar filters ───────────────────────────────────────────────────────────
st.sidebar.header("Filtres")

domaines_dispo = ["(tous)"] + idx["domaines"]
sel_domaine    = st.sidebar.selectbox("Domaine", domaines_dispo)

types_dispo = ["(tous)", "Import", "Alimentation", "Export", "Aggregat"]
sel_type    = st.sidebar.selectbox("Type de flux", types_dispo)

plateformes_dispo = ["(tous)", "BQ", "TD"]
sel_plateforme    = st.sidebar.selectbox("Plateforme", plateformes_dispo)

transverse_only = st.sidebar.checkbox("Flux transverses uniquement")

search = st.sidebar.text_input("Recherche (id_script, description)", placeholder="clients…")

# ── Apply filters ─────────────────────────────────────────────────────────────
flux_list = idx["flux"]

if sel_domaine != "(tous)":
    flux_list = [f for f in flux_list if f["domaine"] == sel_domaine]
if sel_type != "(tous)":
    flux_list = [f for f in flux_list if f["type"] == sel_type]
if sel_plateforme != "(tous)":
    flux_list = [f for f in flux_list if f["plateforme"] == sel_plateforme]
if transverse_only:
    flux_list = [f for f in flux_list if f["is_transverse"]]
if search:
    kw = search.lower()
    flux_list = [
        f for f in flux_list
        if kw in f["id_script"].lower() or kw in f["description"].lower()
    ]

# ── Summary ───────────────────────────────────────────────────────────────────
c1, c2, c3 = st.columns(3)
c1.metric("Flux affichés", len(flux_list))
c2.metric("Flux transverses", sum(1 for f in flux_list if f["is_transverse"]))
c3.metric("Domaines", len({f["domaine"] for f in flux_list}))

st.divider()

# ── Flux list ─────────────────────────────────────────────────────────────────
if not flux_list:
    st.info("Aucun flux ne correspond aux filtres sélectionnés.")
    st.stop()

# Group by domain for display
domain_groups: dict[str, list[dict]] = {}
for f in flux_list:
    domain_groups.setdefault(f["domaine"], []).append(f)

for domaine, flux_du_domaine in sorted(domain_groups.items()):
    with st.expander(f"**{domaine}** — {len(flux_du_domaine)} flux", expanded=(len(domain_groups) == 1)):
        for flux in flux_du_domaine:
            badge_type = {
                "Import":       "🔵",
                "Alimentation": "🟢",
                "Export":       "🟠",
                "Aggregat":     "🟣",
            }.get(flux["type"], "⚪")
            badge_pf = "☁️" if flux["plateforme"] == "BQ" else "🗄️"
            transverse_badge = " 🔗 _transverse_" if flux["is_transverse"] else ""

            col_title, col_pf = st.columns([5, 1])
            with col_title:
                st.markdown(
                    f"{badge_type} **{flux['id_script']}**{transverse_badge}  \n"
                    f"_{flux['description']}_"
                )
            with col_pf:
                st.caption(f"{badge_pf} {flux['plateforme']} · {flux['type']}")

            # Tables référencées
            if flux["tables_referenced"]:
                own = flux["domaine"]
                ext_refs = [r for r in flux["tables_referenced"] if r.get("domaine_owner", own) != own]
                if ext_refs:
                    refs_txt = ", ".join(
                        f"`{r['dataset']}.{r['table']}` ({r.get('domaine_owner', '?')})"
                        for r in ext_refs
                    )
                    st.caption(f"Dépendances transverses : {refs_txt}")

            # YAML viewer
            with st.expander("Voir le YAML", expanded=False):
                try:
                    content = Path(flux["yaml_path"]).read_text(encoding="utf-8")
                    st.code(content, language="yaml")
                except OSError:
                    st.warning("Fichier YAML introuvable.")

            st.divider()
