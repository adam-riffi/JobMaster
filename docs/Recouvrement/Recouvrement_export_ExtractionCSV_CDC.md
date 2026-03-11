# Cahier des Charges — Recouvrement / Export / ExtractionCSV

**Domaine** : Recouvrement
**Type de flux** : Export
**Plateforme cible** : TD
**Statut** : Demande de création
**Date** : 01/03/2026
**Demandeur** : Équipe Data Engineering Télécom

---

## Contexte métier

Extraction quotidienne du SOCLE creances vers un fichier CSV daté pour distribution aux partenaires.

---

## Sources souhaitées

- Table SOCLE : `£TD_SOCLE.creances`

---

## Cibles souhaitées

- Fichier CSV : `C:\data\recouvrement\export/recouvrement_AAAAMMJJ.csv`

---

## Règles de gestion

- Extraire toutes les lignes actives du SOCLE.
- Nommer le fichier avec la date du jour (format AAAAMMJJ).
- Format CSV avec en-têtes.

---

## Fréquence souhaitée

Quotidien — après alimentation SOCLE.

---

## Contraintes techniques

- Le répertoire `C:\data\recouvrement\export` doit exister.
- Purge des exports de plus de 1 mois.

---

## Historique

| Date | Version | Auteur | Commentaire |
|------|---------|--------|-------------|
| 01/03/2026 | 1.0 | Data Engineering | Création initiale |
