# Cahier des Charges — Interconnexion / Aggregat / JournalierSocle

**Domaine** : Interconnexion
**Type de flux** : Aggregat
**Plateforme cible** : TD
**Statut** : Demande de création
**Date** : 01/03/2026
**Demandeur** : Équipe Data Engineering Télécom

---

## Contexte métier

Historisation quotidienne des comptages du SOCLE interconnexion pour suivi de volumétrie.

---

## Sources souhaitées

- Table SOCLE : `£TD_SOCLE.interconnexion`

---

## Cibles souhaitées

- Table historique : `£TD_HISTO.interconnexion_histo`

---

## Règles de gestion

- Insérer une ligne par jour avec le count du SOCLE.
- Ne pas écraser les jours précédents.
- Contrôler que le SOCLE a été mis à jour avant d'agréger.

---

## Fréquence souhaitée

Quotidien — après alimentation SOCLE.

---

## Contraintes techniques

- La table historique doit exister (voir installation).
- Un seul enregistrement par jour autorisé.

---

## Historique

| Date | Version | Auteur | Commentaire |
|------|---------|--------|-------------|
| 01/03/2026 | 1.0 | Data Engineering | Création initiale |
