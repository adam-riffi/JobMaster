# Cahier des Charges — Consommations / Import / Decompression

**Domaine** : Consommations
**Type de flux** : Import
**Plateforme cible** : TD
**Statut** : Demande de création
**Date** : 01/03/2026
**Demandeur** : Équipe Data Engineering Télécom

---

## Contexte métier

Décompression des archives consommations (.gz) reçues depuis la plateforme de médiation avant validation.

---

## Sources souhaitées

- Répertoire source : `C:\data\consommations\in`
- Format : gzip (.csv.gz)

---

## Cibles souhaitées

- Répertoire cible : `C:\data\consommations\work` (fichiers .csv décompressés)

---

## Règles de gestion

- Décompresser chaque fichier .gz individuellement.
- Conserver le fichier source jusqu'à validation.

---

## Fréquence souhaitée

Quotidien — immédiatement après rapatriement.

---

## Contraintes techniques

- Format gzip uniquement. Les autres formats doivent être rejetés.

---

## Historique

| Date | Version | Auteur | Commentaire |
|------|---------|--------|-------------|
| 01/03/2026 | 1.0 | Data Engineering | Création initiale |
