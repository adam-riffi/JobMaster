# Cahier des Charges — Contrats / Import / TraitementBatch

**Domaine** : Contrats
**Type de flux** : Import
**Plateforme cible** : BQ
**Statut** : Demande de création
**Date** : 01/03/2026
**Demandeur** : Équipe Data Engineering Télécom

---

## Contexte métier

Chargement en masse de tous les fichiers contrats validés dans la table staging puis archivage.

---

## Sources souhaitées

- Zone de travail : `C:\data\contrats\work`
- Table staging : `£BQ_TMP.staging_contrats`

---

## Cibles souhaitées

- Table staging chargée : `£BQ_TMP.staging_contrats`
- Fichiers archivés dans `C:\data\contrats\archive`

---

## Règles de gestion

- Charger tous les fichiers en une seule passe (batch).
- Archiver les fichiers traités.
- Purger les archives de plus de 3 mois.

---

## Fréquence souhaitée

Quotidien — après contrôle CSV.

---

## Contraintes techniques

- La table staging doit exister (voir installation).
- En cas d'échec partiel, toute la passe doit être rejouée.

---

## Historique

| Date | Version | Auteur | Commentaire |
|------|---------|--------|-------------|
| 01/03/2026 | 1.0 | Data Engineering | Création initiale |
