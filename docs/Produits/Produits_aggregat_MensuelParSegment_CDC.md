# Cahier des Charges — Produits / Aggregat / MensuelParSegment

**Domaine** : Produits
**Type de flux** : Aggregat
**Plateforme cible** : BQ
**Statut** : Demande de création
**Date** : 01/03/2026
**Demandeur** : Équipe Data Engineering Télécom

---

## Contexte métier

Calcul des agrégats mensuels du SOCLE produits par dimension métier pour le reporting mensuel.

---

## Sources souhaitées

- Table SOCLE : `£BQ_SOCLE.produits`

---

## Cibles souhaitées

- Table agrégat mensuelle : `£BQ_HISTO.produits_aggr_ventes_mensuel`

---

## Règles de gestion

- Supprimer les agrégats du mois courant avant recalcul (idempotent).
- Agréger sur la période AAAAMM en cours.
- Granularité : par segment ou dimension principale.

---

## Fréquence souhaitée

Mensuel — 1er jour du mois suivant.

---

## Contraintes techniques

- Flux idempotent : peut être rejoué sans doublon.
- Le mois en cours ne doit jamais être partiel dans la table agrégat.

---

## Historique

| Date | Version | Auteur | Commentaire |
|------|---------|--------|-------------|
| 01/03/2026 | 1.0 | Data Engineering | Création initiale |
