"""Aleister — Knowledge base : scan et indexation des flux JobMaster.

Parcourt WORKSPACE_ROOT, parse les YAML de chaque flux et extrait les
références SQL (£XX_SOCLE.table, £XX_HISTO.table) pour détecter les
dépendances cross-domaine.

Structure de l'index retourné par `build_index()` :
  {
    "domaines": ["Clients", "Consommations", ...],
    "flux": [
      {
        "id_script": "Clients_Import_RapatriementSFTP",
        "description": "...",
        "domaine": "Clients",
        "type": "Import",            # Import | Alimentation | Export | Aggregat
        "plateforme": "BQ",
        "yaml_path": "...",
        "sql_files": ["..."],
        "tables_referenced": [       # toutes les tables £XX.table trouvées dans les SQL
          {"platform": "BQ", "dataset": "BQ_SOCLE", "table": "clients", "domaine_owner": "Clients"},
          ...
        ],
        "is_transverse": bool,       # True si une table référencée appartient à un autre domaine
      },
      ...
    ],
    "tables": {                      # index inverse : table → flux qui la référencent
      "BQ_SOCLE.clients": ["Clients_Import_...", ...],
      ...
    },
  }
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from aleister.config import WORKSPACE_ROOT


# ── Patterns ──────────────────────────────────────────────────────────────────
# Capture £BQ_SOCLE.clients, £TD_HISTO.cdr_voix, etc.
_TABLE_RE = re.compile(r"£(BQ|TD)_(SOCLE|HISTO|TMP|VUES|SOURCE)\.(\w+)")

# Mapping table_name → domaine propriétaire (socle tables)
# Construit dynamiquement depuis l'arborescence des workspaces.
_SOCLE_TABLE_TO_DOMAIN: dict[str, str] = {}


# ── Helpers ───────────────────────────────────────────────────────────────────
def _build_socle_index(workspace: Path) -> dict[str, str]:
    """Associe chaque table SOCLE à son domaine propriétaire.

    Stratégie : cherche les fichiers SQL de création dans Alimentation/installation/sql/
    et Import/installation/sql/ et déduit le domaine depuis le chemin.
    """
    mapping: dict[str, str] = {}
    for create_sql in workspace.rglob("*_creation_table_socle.*"):
        domaine = create_sql.parts[len(workspace.parts)]
        for m in _TABLE_RE.finditer(create_sql.read_text(encoding="utf-8", errors="ignore")):
            _, dataset, table = m.groups()
            if dataset == "SOCLE":
                mapping[table] = domaine
    return mapping


def _extract_tables(sql_paths: list[Path]) -> list[dict]:
    """Extrait toutes les références £XX_DATASET.table depuis des fichiers SQL."""
    seen: set[str] = set()
    refs: list[dict] = []
    for path in sql_paths:
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for m in _TABLE_RE.finditer(content):
            platform, dataset, table = m.groups()
            key = f"{platform}_{dataset}.{table}"
            if key not in seen:
                seen.add(key)
                refs.append({"platform": platform, "dataset": f"{platform}_{dataset}", "table": table})
    return refs


def _parse_yaml_meta(yaml_path: Path) -> dict:
    """Extrait id_script, description et plateforme depuis un YAML."""
    try:
        data = yaml.safe_load(yaml_path.read_text(encoding="utf-8", errors="ignore"))
        script = data.get("script", {}) if data else {}
        return {
            "id_script":   script.get("id_script", yaml_path.stem),
            "description": script.get("description", ""),
        }
    except Exception:
        return {"id_script": yaml_path.stem, "description": ""}


def _detect_platform(yaml_path: Path, meta: dict) -> str:
    """Déduit la plateforme (BQ/TD) depuis le contenu YAML."""
    try:
        content = yaml_path.read_text(encoding="utf-8", errors="ignore")
        if "Plateforme: BQ" in content or "PlateformeSource: BQ" in content:
            return "BQ"
        if "Plateforme: TD" in content or "PlateformeSource: TD" in content:
            return "TD"
    except OSError:
        pass
    return "?"


# ── Public API ────────────────────────────────────────────────────────────────
def build_index(workspace: Path | None = None) -> dict[str, Any]:
    """Construit l'index complet des flux depuis le workspace.

    Returns a dict with keys: domaines, flux, tables.
    """
    root = workspace or WORKSPACE_ROOT
    if not root.exists():
        return {"domaines": [], "flux": [], "tables": {}}

    # Build socle → domain mapping from installation scripts
    socle_map = _build_socle_index(root)

    flux_list: list[dict] = []
    tables_index: dict[str, list[str]] = {}

    for domain_dir in sorted(d for d in root.iterdir() if d.is_dir()):
        domaine = domain_dir.name
        for type_dir in sorted(t for t in domain_dir.iterdir() if t.is_dir()):
            flow_type = type_dir.name
            if flow_type not in ("Import", "Alimentation", "Export", "Aggregat"):
                continue
            config_dir = type_dir / "config"
            sql_dir    = type_dir / "sql"
            if not config_dir.exists():
                continue

            for yaml_path in sorted(config_dir.glob("*.yml")):
                # Skip installation configs (they live in installation/config/)
                meta = _parse_yaml_meta(yaml_path)
                platform = _detect_platform(yaml_path, meta)

                # Collect SQL files for this YAML (same sql_dir, same stem prefix)
                sql_files: list[Path] = []
                if sql_dir.exists():
                    sql_files = list(sql_dir.glob("*.gql")) + list(sql_dir.glob("*.dql"))

                table_refs = _extract_tables(sql_files)

                # Enrich with domain ownership
                for ref in table_refs:
                    if ref["dataset"].endswith("_SOCLE"):
                        owner = socle_map.get(ref["table"], domaine)
                        ref["domaine_owner"] = owner
                    else:
                        ref["domaine_owner"] = domaine

                is_transverse = any(
                    ref.get("domaine_owner", domaine) != domaine
                    for ref in table_refs
                )

                flux = {
                    "id_script":         meta["id_script"],
                    "description":       meta["description"],
                    "domaine":           domaine,
                    "type":              flow_type,
                    "plateforme":        platform,
                    "yaml_path":         str(yaml_path),
                    "sql_files":         [str(p) for p in sql_files],
                    "tables_referenced": table_refs,
                    "is_transverse":     is_transverse,
                }
                flux_list.append(flux)

                # Update inverse index
                for ref in table_refs:
                    key = f"{ref['dataset']}.{ref['table']}"
                    tables_index.setdefault(key, []).append(meta["id_script"])

    domaines = sorted({f["domaine"] for f in flux_list})

    return {
        "domaines": domaines,
        "flux":     flux_list,
        "tables":   tables_index,
    }
