# Cahier des Charges — Finance / Alimentation / EnrichissementTransverse

**Domaine** : Finance
**Type de flux** : Alimentation
**Plateforme cible** : BQ
**Statut** : Demande de création
**Date** : 01/03/2026
**Demandeur** : Équipe Data Engineering Télécom

---

## Contexte métier

Enrichissement du SOCLE comptes_financiers avec des données provenant d'autres domaines via jointures SQL transverses.

---

## Sources souhaitées

- Table SOCLE locale : `£BQ_SOCLE.comptes_financiers`
- Table transverse : `£BQ_SOCLE.factures` (domaine Facturation)
- Table transverse : `£BQ_SOCLE.paiements` (domaine Paiements)
- Table transverse : `£TD_SOCLE.creances` (domaine Recouvrement)

---

## Cibles souhaitées

- Table enrichie : `£BQ_TMP.comptes_financiers_enrichi`

---

## Règles de gestion

- Joindre les tables des domaines référencés.
- Ne pas modifier les données SOCLE originales.
- Stocker le résultat en table temporaire pour les agrégats.

---

## Dépendances transverses

Ce flux est **transverse** : il emprunte des tables appartenant à d'autres domaines.
Toute évolution de ces tables peut impacter ce flux.

- `BQ_SOCLE.factures` (domaine **Facturation**)
- `BQ_SOCLE.paiements` (domaine **Paiements**)
- `TD_SOCLE.creances` (domaine **Recouvrement**)


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
