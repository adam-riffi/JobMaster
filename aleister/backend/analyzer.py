"""Aleister — Analyse d'impact.

Identifie tous les flux qui référencent une table donnée,
en distinguant les dépendances directes (même domaine) et
transverses (autre domaine).
"""

from __future__ import annotations

from typing import Any

from aleister.backend.knowledge_base import build_index


def analyze_impact(
    table_name: str,
    dataset: str | None = None,
    index: dict | None = None,
) -> dict[str, Any]:
    """Retourne tous les flux impactés par l'évolution d'une table.

    Args:
        table_name: nom de la table (ex. "clients", "cdr_voix").
        dataset:    dataset de la table (ex. "BQ_SOCLE"). Si None, cherche dans tous.
        index:      index pré-construit (évite un recalcul). Si None, reconstruit.

    Returns:
        {
          "table": "BQ_SOCLE.clients",
          "flux_directs":    [...],   # flux du même domaine que la table
          "flux_transverses": [...],  # flux d'autres domaines
          "total": int,
        }
    """
    idx = index or build_index()

    # Normalise la clé de recherche
    search_key = f"{dataset}.{table_name}" if dataset else table_name

    matching_flux: list[dict] = []

    for flux in idx["flux"]:
        for ref in flux["tables_referenced"]:
            key = f"{ref['dataset']}.{ref['table']}"
            if search_key.lower() in key.lower():
                matching_flux.append({
                    "flux": flux,
                    "via": key,
                    "is_transverse": ref.get("domaine_owner", flux["domaine"]) != flux["domaine"],
                })
                break  # une correspondance suffit par flux

    # Détermine le domaine propriétaire de la table
    owner_domain: str | None = None
    for flux in idx["flux"]:
        for ref in flux["tables_referenced"]:
            key = f"{ref['dataset']}.{ref['table']}"
            if search_key.lower() in key.lower() and ref.get("domaine_owner"):
                owner_domain = ref["domaine_owner"]
                break
        if owner_domain:
            break

    flux_directs = [
        item for item in matching_flux
        if item["flux"]["domaine"] == owner_domain
    ]
    flux_transverses = [
        item for item in matching_flux
        if item["flux"]["domaine"] != owner_domain
    ]

    return {
        "table":             search_key,
        "domaine_owner":     owner_domain,
        "flux_directs":      flux_directs,
        "flux_transverses":  flux_transverses,
        "total":             len(matching_flux),
    }


def list_tables(index: dict | None = None) -> list[str]:
    """Retourne la liste triée de toutes les tables référencées dans le workspace."""
    idx = index or build_index()
    return sorted(idx["tables"].keys())
