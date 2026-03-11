"""Aleister — Génération de documentation.

Lit les flux de la knowledge base et produit :
  - Des CDCs Markdown (cahiers des charges pré-implémentation)
  - Des fiches de flux (documentation post-implémentation)
  - Un index global du domaine en Markdown
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from aleister.config import DOCS_ROOT
from aleister.backend.knowledge_base import build_index


def _read_cdc(yaml_path: str) -> str | None:
    """Lit le CDC Markdown associé à un YAML de flux."""
    yp = Path(yaml_path)
    # Déduit le chemin CDC depuis le chemin YAML
    # workspaces/Domaine/Type/config/Domaine_type_Nom.yml
    # → docs/Domaine/Domaine_type_Nom_CDC.md
    try:
        parts = yp.parts
        # find "config" in path
        config_idx = parts.index("config") if "config" in parts else -1
        if config_idx < 0:
            return None
        domaine = parts[config_idx - 2]  # workspaces/<Domaine>/<Type>/config/
        stem = yp.stem
        cdc_path = DOCS_ROOT / domaine / f"{stem}_CDC.md"
        if cdc_path.exists():
            return cdc_path.read_text(encoding="utf-8")
    except (ValueError, IndexError, OSError):
        pass
    return None


def flux_to_markdown(flux: dict) -> str:
    """Génère une fiche Markdown pour un flux donné."""
    lines = [
        f"# {flux['id_script']}",
        "",
        f"**Domaine** : {flux['domaine']}  ",
        f"**Type** : {flux['type']}  ",
        f"**Plateforme** : {flux['plateforme']}  ",
        f"**Transverse** : {'Oui' if flux['is_transverse'] else 'Non'}",
        "",
        "## Description",
        "",
        flux["description"] or "_Aucune description disponible._",
        "",
    ]

    if flux["tables_referenced"]:
        lines += [
            "## Tables référencées",
            "",
        ]
        for ref in flux["tables_referenced"]:
            owner = ref.get("domaine_owner", flux["domaine"])
            tag = " **(transverse)**" if owner != flux["domaine"] else ""
            lines.append(f"- `{ref['dataset']}.{ref['table']}`  (domaine : {owner}){tag}")
        lines.append("")

    if flux["sql_files"]:
        lines += [
            "## Scripts SQL",
            "",
        ]
        for sql in flux["sql_files"]:
            lines.append(f"- `{Path(sql).name}`")
        lines.append("")

    return "\n".join(lines)


def domain_index_markdown(domaine: str, index: dict | None = None) -> str:
    """Génère un index Markdown de tous les flux d'un domaine."""
    idx = index or build_index()
    flux_domaine = [f for f in idx["flux"] if f["domaine"] == domaine]

    lines = [f"# Domaine : {domaine}", "", f"**{len(flux_domaine)} flux indexés**", ""]

    for flow_type in ("Import", "Alimentation", "Export", "Aggregat"):
        type_flux = [f for f in flux_domaine if f["type"] == flow_type]
        if not type_flux:
            continue
        lines += [f"## {flow_type}", ""]
        for f in type_flux:
            transverse = " _(transverse)_" if f["is_transverse"] else ""
            lines.append(f"- **{f['id_script']}**{transverse} — {f['description']}")
        lines.append("")

    return "\n".join(lines)


def export_domain_docs(domaine: str, output_dir: Path | None = None) -> list[Path]:
    """Exporte la documentation complète d'un domaine dans output_dir."""
    out = output_dir or (DOCS_ROOT / domaine / "generated")
    out.mkdir(parents=True, exist_ok=True)

    idx = build_index()
    written: list[Path] = []

    # Index global du domaine
    idx_path = out / f"{domaine}_index.md"
    idx_path.write_text(domain_index_markdown(domaine, idx), encoding="utf-8")
    written.append(idx_path)

    # Fiche par flux
    for flux in [f for f in idx["flux"] if f["domaine"] == domaine]:
        fiche_path = out / f"{flux['id_script']}_fiche.md"
        fiche_path.write_text(flux_to_markdown(flux), encoding="utf-8")
        written.append(fiche_path)

    return written
