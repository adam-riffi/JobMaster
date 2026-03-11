# Cahier des Charges — Incidents / Alimentation / UpsertSocle

**Domaine** : Incidents
**Type de flux** : Alimentation
**Plateforme cible** : TD
**Statut** : Demande de création
**Date** : 01/03/2026
**Demandeur** : Équipe Data Engineering Télécom

---

## Contexte métier

Alimentation du SOCLE incidents depuis la staging par opération MERGE (UPSERT). Mise à jour des existants et insertion des nouveaux.

---

## Sources souhaitées

- Table staging : `£TD_TMP.staging_incidents`

---

## Cibles souhaitées

- Table SOCLE : `£TD_SOCLE.incidents`
- Vue métier : `£TD_VUES.incidents`

---

## Règles de gestion

- Clé de jointure : `id_incident`
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
