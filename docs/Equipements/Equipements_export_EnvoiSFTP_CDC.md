# Cahier des Charges — Equipements / Export / EnvoiSFTP

**Domaine** : Equipements
**Type de flux** : Export
**Plateforme cible** : TD
**Statut** : Demande de création
**Date** : 01/03/2026
**Demandeur** : Équipe Data Engineering Télécom

---

## Contexte métier

Envoi des fichiers CSV equipements extraits vers le SFTP de distribution partenaire.

---

## Sources souhaitées

- Répertoire source : `C:\data\equipements\export`

---

## Cibles souhaitées

- SFTP destination : `sftp://distribution/equipements/out`

---

## Règles de gestion

- Envoyer uniquement les fichiers du jour.
- Vérifier la présence de fichiers avant envoi.
- Purger les exports locaux après envoi réussi.

---

## Fréquence souhaitée

Quotidien — après extraction CSV.

---

## Contraintes techniques

- Connexion SFTP sécurisée requise.
- En cas d'échec d'envoi, conserver le fichier local.

---

## Historique

| Date | Version | Auteur | Commentaire |
|------|---------|--------|-------------|
| 01/03/2026 | 1.0 | Data Engineering | Création initiale |
