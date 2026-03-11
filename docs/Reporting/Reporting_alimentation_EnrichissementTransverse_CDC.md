# Cahier des Charges — Reporting / Alimentation / EnrichissementTransverse

**Domaine** : Reporting
**Type de flux** : Alimentation
**Plateforme cible** : BQ
**Statut** : Demande de création
**Date** : 01/03/2026
**Demandeur** : Équipe Data Engineering Télécom

---

## Contexte métier

Enrichissement du SOCLE kpi_global avec des données provenant d'autres domaines via jointures SQL transverses.

---

## Sources souhaitées

- Table SOCLE locale : `£BQ_SOCLE.kpi_global`
- Table transverse : `£BQ_SOCLE.clients` (domaine Clients)
- Table transverse : `£BQ_SOCLE.factures` (domaine Facturation)
- Table transverse : `£BQ_SOCLE.contrats` (domaine Contrats)
- Table transverse : `£TD_SOCLE.cdr_voix` (domaine Consommations)

---

## Cibles souhaitées

- Table enrichie : `£BQ_TMP.kpi_global_enrichi`

---

## Règles de gestion

- Joindre les tables des domaines référencés.
- Ne pas modifier les données SOCLE originales.
- Stocker le résultat en table temporaire pour les agrégats.

---

## Dépendances transverses

Ce flux est **transverse** : il emprunte des tables appartenant à d'autres domaines.
Toute évolution de ces tables peut impacter ce flux.

- `BQ_SOCLE.clients` (domaine **Clients**)
- `BQ_SOCLE.factures` (domaine **Facturation**)
- `BQ_SOCLE.contrats` (domaine **Contrats**)
- `TD_SOCLE.cdr_voix` (domaine **Consommations**)


## Fréquence souhaitée

Hebdomadaire — chaque dimanche.

---

## Contraintes techniques

- Les tables des domaines partenaires doivent être à jour.
- Flux TRANSVERSE : toute évolution des tables empruntées impacte ce flux.

---

## Historique

| Date | Version | Auteur | Commentaire |
|------|---------|--------|-------------|
| 01/03/2026 | 1.0 | Data Engineering | Création initiale |
