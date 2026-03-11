# Cahier des Charges — Incidents / Alimentation / ChargementsParalleles

**Domaine** : Incidents
**Type de flux** : Alimentation
**Plateforme cible** : TD
**Statut** : Demande de création
**Date** : 01/03/2026
**Demandeur** : Équipe Data Engineering Télécom

---

## Contexte métier

Chargement simultané du SOCLE et de la table historique incidents pour optimiser les temps de traitement.

---

## Sources souhaitées

- Table staging : `£TD_TMP.staging_incidents`

---

## Cibles souhaitées

- SOCLE : `£TD_SOCLE.incidents`
- Historique : `£TD_HISTO.incidents_histo`

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
