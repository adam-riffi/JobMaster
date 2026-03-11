# Cahier des Charges — Reporting / Import / RapatriementSFTP

**Domaine** : Reporting
**Type de flux** : Import
**Plateforme cible** : BQ
**Statut** : Demande de création
**Date** : 01/03/2026
**Demandeur** : Équipe Data Engineering Télécom

---

## Contexte métier

Rapatriement quotidien des fichiers reporting depuis le serveur SFTP du partenaire vers la zone d'entrée locale.

---

## Sources souhaitées

- SFTP source : `sftp://bi-platform/kpi/in`
- Format : CSV (séparateur `;`, encodage UTF-8)
- Masque fichier : `^kpi_\d{8}\.csv$`

---

## Cibles souhaitées

- Répertoire local : `C:\data\reporting\in`

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
- Le répertoire `C:\data\reporting\in` doit exister avant exécution.

---

## Historique

| Date | Version | Auteur | Commentaire |
|------|---------|--------|-------------|
| 01/03/2026 | 1.0 | Data Engineering | Création initiale |
