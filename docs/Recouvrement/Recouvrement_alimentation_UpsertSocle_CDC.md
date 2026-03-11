# Cahier des Charges — Recouvrement / Alimentation / UpsertSocle

**Domaine** : Recouvrement
**Type de flux** : Alimentation
**Plateforme cible** : TD
**Statut** : Demande de création
**Date** : 01/03/2026
**Demandeur** : Équipe Data Engineering Télécom

---

## Contexte métier

Alimentation du SOCLE creances depuis la staging par opération MERGE (UPSERT). Mise à jour des existants et insertion des nouveaux.

---

## Sources souhaitées

- Table staging : `£TD_TMP.staging_creances`

---

## Cibles souhaitées

- Table SOCLE : `£TD_SOCLE.creances`
- Vue métier : `£TD_VUES.creances`

---

## Règles de gestion

- Clé de jointure : `id_creance`
- MERGE : UPDATE si existant, INSERT si nouveau.
- Mettre à jour `date_maj` à chaque modification.
- Créer/rafraîchir la vue métier après chaque run.

---

## Fréquence souhaitée

Quotidien — après chargement staging.

---

## Contraintes techniques

- La staging doit être peuplée (contrôle via FLAG avant merge).
- La vue ne doit jamais pointer sur une table vide.

---

## Historique

| Date | Version | Auteur | Commentaire |
|------|---------|--------|-------------|
| 01/03/2026 | 1.0 | Data Engineering | Création initiale |
