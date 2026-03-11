# Cahier des Charges — Consommations / Import / RapatriementSFTP

**Domaine** : Consommations
**Type de flux** : Import
**Plateforme cible** : TD
**Statut** : Demande de création
**Date** : 01/03/2026
**Demandeur** : Équipe Data Engineering Télécom

---

## Contexte métier

Rapatriement quotidien des fichiers consommations depuis le serveur SFTP du partenaire vers la zone d'entrée locale.

---

## Sources souhaitées

- SFTP source : `sftp://mediation-platform/cdr/voix`
- Format : CSV (séparateur `|`, encodage UTF-8)
- Masque fichier : `^cdr_voix_\d{8}\.csv\.gz$`

---

## Cibles souhaitées

- Répertoire local : `C:\data\consommations\in`

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
- Le répertoire `C:\data\consommations\in` doit exister avant exécution.

---

## Historique

| Date | Version | Auteur | Commentaire |
|------|---------|--------|-------------|
| 01/03/2026 | 1.0 | Data Engineering | Création initiale |
