# Cahier des Charges — Reporting / Alimentation / ChargementsParalleles

**Domaine** : Reporting
**Type de flux** : Alimentation
**Plateforme cible** : BQ
**Statut** : Demande de création
**Date** : 01/03/2026
**Demandeur** : Équipe Data Engineering Télécom

---

## Contexte métier

Chargement simultané du SOCLE et de la table historique reporting pour optimiser les temps de traitement.

---

## Sources souhaitées

- Table staging : `£BQ_TMP.staging_kpi_global`

---

## Cibles souhaitées

- SOCLE : `£BQ_SOCLE.kpi_global`
- Historique : `£BQ_HISTO.kpi_global_histo`

---

## Règles de gestion

- Exécuter le MERGE SOCLE et l'INSERT HISTO en parallèle.
- Les deux opérations sont indépendantes.
- Le flux global échoue si l'une des deux échoue.

---

## Fréquence souhaitée

Quotidien — en remplacement du chargement séquentiel sur les volumes importants.

---

## Contraintes techniques

- Aucune dépendance entre SOCLE et HISTO pour ce flux.
- Rollback manuel si l'une des deux opérations échoue à mi-course.

---

## Historique

| Date | Version | Auteur | Commentaire |
|------|---------|--------|-------------|
| 01/03/2026 | 1.0 | Data Engineering | Création initiale |
