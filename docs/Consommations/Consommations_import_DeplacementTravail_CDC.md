# Cahier des Charges — Consommations / Import / DeplacementTravail

**Domaine** : Consommations
**Type de flux** : Import
**Plateforme cible** : TD
**Statut** : Demande de création
**Date** : 01/03/2026
**Demandeur** : Équipe Data Engineering Télécom

---

## Contexte métier

Déplacement des fichiers consommations validés de la zone d'entrée vers la zone de travail pour traitement.

---

## Sources souhaitées

- Répertoire source : `C:\data\consommations\in`
- Masque : `^cdr_voix_\d{8}\.csv\.gz$`

---

## Cibles souhaitées

- Répertoire cible : `C:\data\consommations\work`

---

## Règles de gestion

- Déplacer uniquement les fichiers correspondant au masque.
- Ne laisser aucun fichier en zone d'entrée après déplacement.

---

## Fréquence souhaitée

Quotidien — après le rapatriement SFTP.

---

## Contraintes techniques

- Répertoire `C:\data\consommations\work` doit exister.
- Aucun fichier en doublon accepté en zone de travail.

---

## Historique

| Date | Version | Auteur | Commentaire |
|------|---------|--------|-------------|
| 01/03/2026 | 1.0 | Data Engineering | Création initiale |
