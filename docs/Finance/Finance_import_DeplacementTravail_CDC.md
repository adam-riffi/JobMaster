# Cahier des Charges — Finance / Import / DeplacementTravail

**Domaine** : Finance
**Type de flux** : Import
**Plateforme cible** : BQ
**Statut** : Demande de création
**Date** : 01/03/2026
**Demandeur** : Équipe Data Engineering Télécom

---

## Contexte métier

Déplacement des fichiers finance validés de la zone d'entrée vers la zone de travail pour traitement.

---

## Sources souhaitées

- Répertoire source : `C:\data\finance\in`
- Masque : `^ecritures_\d{8}\.csv$`

---

## Cibles souhaitées

- Répertoire cible : `C:\data\finance\work`

---

## Règles de gestion

- Déplacer uniquement les fichiers correspondant au masque.
- Ne laisser aucun fichier en zone d'entrée après déplacement.

---

## Fréquence souhaitée

Quotidien — après le rapatriement SFTP.

---

## Contraintes techniques

- Répertoire `C:\data\finance\work` doit exister.
- Aucun fichier en doublon accepté en zone de travail.

---

## Historique

| Date | Version | Auteur | Commentaire |
|------|---------|--------|-------------|
| 01/03/2026 | 1.0 | Data Engineering | Création initiale |
