# Cahier des Charges — Fraude / Import / RapatriementSFTP

**Domaine** : Fraude
**Type de flux** : Import
**Plateforme cible** : TD
**Statut** : Demande de création
**Date** : 01/03/2026
**Demandeur** : Équipe Data Engineering Télécom

---

## Contexte métier

Rapatriement quotidien des fichiers fraude depuis le serveur SFTP du partenaire vers la zone d'entrée locale.

---

## Sources souhaitées

- SFTP source : `sftp://fraud-engine/alertes/in`
- Format : CSV (séparateur `|`, encodage UTF-8)
- Masque fichier : `^fraude_alertes_\d{8}\.csv$`

---

## Cibles souhaitées

- Répertoire local : `C:\data\fraude\in`

---

## Règles de gestion

- Récupérer tous les fichiers correspondant au masque.
- Ne pas supprimer les fichiers sur le SFTP source.
- En cas d'échec de connexion, le flux doit échouer et alerter.

---

## Fréquence souhaitée

Quotidien — déclenchement à 06h00.

---

## Contraintes techniques

- Connexion SFTP sécurisée (clé SSH).
- Timeout de connexion : 30 secondes.
- Le répertoire `C:\data\fraude\in` doit exister avant exécution.

---

## Historique

| Date | Version | Auteur | Commentaire |
|------|---------|--------|-------------|
| 01/03/2026 | 1.0 | Data Engineering | Création initiale |
