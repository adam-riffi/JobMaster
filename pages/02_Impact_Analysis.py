"""Aleister — Analyse d'impact.

Identifie tous les flux affectés par l'évolution d'une table donnée.
Met en évidence les dépendances transverses (flux d'autres domaines).
"""

import streamlit as st

from aleister.backend.knowledge_base import build_index
from aleister.backend.analyzer import analyze_impact, list_tables

st.set_page_config(
    page_title="Aleister — Analyse d'impact",
    page_icon="🔍",
    layout="wide",
)

st.title("🔍 Analyse d'impact")
st.caption(
    "Sélectionne une table pour identifier tous les flux qui la référencent, "
    "y compris les flux **transverses** cross-domaine."
)


# ── Build / cache index ───────────────────────────────────────────────────────
@st.cache_data(ttl=120, show_spinner="Indexation du workspace…")
def _load_index() -> dict:
    return build_index()


idx = _load_index()

if not idx["flux"]:
    st.warning("Aucun flux trouvé. Vérifiez WORKSPACE_ROOT dans votre .env.")
    st.stop()

# ── Table selector ────────────────────────────────────────────────────────────
all_tables = list_tables(idx)

col_search, col_select = st.columns([2, 3])

with col_search:
    filter_text = st.text_input(
        "Filtrer les tables",
        placeholder="clients, cdr_voix…",
        help="Tape quelques lettres pour réduire la liste.",
    )

filtered_tables = (
    [t for t in all_tables if filter_text.lower() in t.lower()]
    if filter_text
    else all_tables
)

with col_select:
    if not filtered_tables:
        st.warning("Aucune table ne correspond au filtre.")
        st.stop()
    selected_table = st.selectbox("Table à analyser", filtered_tables)

st.divider()

# ── Run analysis ──────────────────────────────────────────────────────────────
if selected_table:
    result = analyze_impact(selected_table, index=idx)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Table analysée", selected_table.split(".")[-1])
    c2.metric("Domaine propriétaire", result["domaine_owner"] or "?")
    c3.metric("Flux directs",     len(result["flux_directs"]))
    c4.metric("Flux transverses", len(result["flux_transverses"]),
              delta=f"{len(result['flux_transverses'])} cross-domaine" if result["flux_transverses"] else None,
              delta_color="inverse" if result["flux_transverses"] else "off")

    st.divider()

    if result["total"] == 0:
        st.success(f"Aucun flux ne référence `{selected_table}`. Évolution sans impact.")
        st.stop()

    # ── Direct flux ───────────────────────────────────────────────────────────
    if result["flux_directs"]:
        st.subheader(f"Flux directs — domaine {result['domaine_owner']}")
        st.caption("Ces flux appartiennent au même domaine que la table. Impact prévisible.")

        for item in result["flux_directs"]:
            f = item["flux"]
            badge = {"Import": "🔵", "Alimentation": "🟢", "Export": "🟠", "Aggregat": "🟣"}.get(f["type"], "⚪")
            st.markdown(
                f"{badge} **{f['id_script']}** — {f['type']} — {f['plateforme']}  \n"
                f"_{f['description']}_  \n"
                f"Via : `{item['via']}`"
            )
            st.divider()

    # ── Transverse flux ───────────────────────────────────────────────────────
    if result["flux_transverses"]:
        st.subheader("Flux transverses — autres domaines")
        st.warning(
            f"{len(result['flux_transverses'])} flux d'autres domaines référencent cette table. "
            "Ces dépendances sont souvent invisibles sans analyse explicite.",
            icon="⚠️",
        )

        for item in result["flux_transverses"]:
            f = item["flux"]
            badge = {"Import": "🔵", "Alimentation": "🟢", "Export": "🟠", "Aggregat": "🟣"}.get(f["type"], "⚪")
            st.markdown(
                f"{badge} **{f['id_script']}** — domaine **{f['domaine']}** — {f['type']} — {f['plateforme']}  \n"
                f"_{f['description']}_  \n"
                f"Via : `{item['via']}`"
            )
            st.divider()

    # ── Export report ─────────────────────────────────────────────────────────
    st.subheader("Exporter le rapport")
    lines = [
        f"# Rapport d'impact — `{selected_table}`\n",
        f"**Domaine propriétaire** : {result['domaine_owner'] or '?'}  ",
        f"**Flux directs** : {len(result['flux_directs'])}  ",
        f"**Flux transverses** : {len(result['flux_transverses'])}  ",
        f"**Total impactés** : {result['total']}\n",
        "---\n",
        "## Flux directs\n",
    ]
    for item in result["flux_directs"]:
        f = item["flux"]
        lines.append(f"- **{f['id_script']}** ({f['type']}/{f['plateforme']}) — via `{item['via']}`")
    lines += ["\n## Flux transverses\n"]
    for item in result["flux_transverses"]:
        f = item["flux"]
        lines.append(
            f"- **{f['id_script']}** (domaine {f['domaine']} / {f['type']} / {f['plateforme']}) — via `{item['via']}`"
        )

    report_md = "\n".join(lines)
    st.download_button(
        label="Télécharger le rapport (Markdown)",
        data=report_md.encode("utf-8"),
        file_name=f"impact_{selected_table.replace('.', '_')}.md",
        mime="text/markdown",
    )
