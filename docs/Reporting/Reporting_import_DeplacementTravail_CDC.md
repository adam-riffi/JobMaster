# Cahier des Charges — Reporting / Import / DeplacementTravail

**Domaine** : Reporting
**Type de flux** : Import
**Plateforme cible** : BQ
**Statut** : Demande de création
**Date** : 01/03/2026
**Demandeur** : Équipe Data Engineering Télécom

---

## Contexte métier

Déplacement des fichiers reporting validés de la zone d'entrée vers la zone de travail pour traitement.

---

## Sources souhaitées

- Répertoire source : `C:\data\reporting\in`
- Masque : `^kpi_\d{8}\.csv$`

---

## Cibles souhaitées

- Répertoire cible : `C:\data\reporting\work`

---

## Règles de gestion

- Déplacer uniquement les fichiers correspondant au masque.
- Ne laisser aucun fichier en zone d'entrée après déplacement.

---

## Fréquence souhaitée

Quotidien — après le rapatriement SFTP.

---

## Contraintes techniques

- Répertoire `C:\data\reporting\work` doit exister.
- Aucun fichier en doublon accepté en zone de travail.

---

## Historique

| Date | Version | Auteur | Commentaire |
|------|---------|--------|-------------|
| 01/03/2026 | 1.0 | Data Engineering | Création initiale |
