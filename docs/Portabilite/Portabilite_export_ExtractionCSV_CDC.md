# Cahier des Charges — Portabilite / Export / ExtractionCSV

**Domaine** : Portabilite
**Type de flux** : Export
**Plateforme cible** : TD
**Statut** : Demande de création
**Date** : 01/03/2026
**Demandeur** : Équipe Data Engineering Télécom

---

## Contexte métier

Extraction quotidienne du SOCLE portages vers un fichier CSV daté pour distribution aux partenaires.

---

## Sources souhaitées

- Table SOCLE : `£TD_SOCLE.portages`

---

## Cibles souhaitées

- Fichier CSV : `C:\data\portabilite\export/portabilite_AAAAMMJJ.csv`

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

- Le répertoire `C:\data\portabilite\export` doit exister.
- Purge des exports de plus de 1 mois.

---

## Historique

| Date | Version | Auteur | Commentaire |
|------|---------|--------|-------------|
| 01/03/2026 | 1.0 | Data Engineering | Création initiale |
