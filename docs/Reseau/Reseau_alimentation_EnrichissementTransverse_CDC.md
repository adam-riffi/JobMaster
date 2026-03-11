# Cahier des Charges — Reseau / Alimentation / EnrichissementTransverse

**Domaine** : Reseau
**Type de flux** : Alimentation
**Plateforme cible** : TD
**Statut** : Demande de création
**Date** : 01/03/2026
**Demandeur** : Équipe Data Engineering Télécom

---

## Contexte métier

Enrichissement du SOCLE sites_reseau avec des données provenant d'autres domaines via jointures SQL transverses.

---

## Sources souhaitées

- Table SOCLE locale : `£TD_SOCLE.sites_reseau`
- Table transverse : `£TD_SOCLE.incidents` (domaine Incidents)
- Table transverse : `£TD_SOCLE.equipements` (domaine Equipements)

---

## Cibles souhaitées

- Table enrichie : `£TD_TMP.sites_reseau_enrichi`

---

## Règles de gestion

- Joindre les tables des domaines référencés.
- Ne pas modifier les données SOCLE originales.
- Stocker le résultat en table temporaire pour les agrégats.

---

## Dépendances transverses

Ce flux est **transverse** : il emprunte des tables appartenant à d'autres domaines.
Toute évolution de ces tables peut impacter ce flux.

- `TD_SOCLE.incidents` (domaine **Incidents**)
- `TD_SOCLE.equipements` (domaine **Equipements**)


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
